import csv
import cv2
import numpy as np

def resize_image(image, scale_factor=0.5):
    current_height, current_width = image.shape[:2]
    new_width = int(current_width * scale_factor)
    new_height = int(current_height * scale_factor)
    resized_image = cv2.resize(image, (new_width, new_height))
    return resized_image

def find_most_prominent_color(image, circle_center, circle_radius):
    x, y = circle_center
    roi = image[y - circle_radius:y + circle_radius, x - circle_radius:x + circle_radius]
    mean_bgr = np.mean(roi, axis=(0, 1))
    return mean_bgr.astype(int)

def get_video_timestamp(frame_number, fps):
    seconds = frame_number / fps
    return int(seconds)

def write_entry_exit_times_to_csv(quadrant, csv_path, entry_exit_times):
    with open(csv_path, mode='a', newline='') as file:
        csv_writer = csv.writer(file)

        # Check if the file is empty
        if file.tell() == 0:
            csv_writer.writerow(['Quadrant', 'Entry Time', 'Exit Time'])

        for entry, exit in entry_exit_times:
            # Only write to CSV if the difference is more than 4
            if exit - entry > 4:
                csv_writer.writerow([quadrant, entry, exit])

def find_ball_color(bgr_values):
    color_ranges = {
        'BlueBall': [(70, 0, 0), (110, 255, 255)],
        'OrangeBall': [(80, 100, 200), (255, 255, 255)],
        'YellowBall': [(0, 255, 255), (0, 0, 255)],
        'WhiteBall': [(0, 170, 180), (149, 255, 255)]
    }

    for ball, (lower, upper) in color_ranges.items():
        if all(lower[i] <= bgr_values[i] <= upper[i] for i in range(3)):
            return ball

    return 'Unknown'

def calculate_radius_video(quadrant, video_path, output_csv_path):
    cap = cv2.VideoCapture(video_path)
    circle_coordinates = []
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = 0
    ball_in_frame = False
    entry_time = 0
    exit_time = 0
    entry_exit_times = []

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        frame_count += 1

        cv2.imshow("Original Frame", frame)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (9, 9), 0)

        circles = cv2.HoughCircles(
            blurred,
            cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=50,
            param1=60,
            param2=30,
            minRadius=25,
            maxRadius=100
        )

        if circles is not None:
            circles = np.uint16(np.around(circles))

            for i in circles[0, :]:
                circle_coordinates.append((i[0], i[1]))

                if not ball_in_frame:
                    entry_time = get_video_timestamp(frame_count, fps)
                    # print("entry time:", entry_time)
                    ball_in_frame = True

                mask = np.zeros_like(gray)
                cv2.circle(mask, (i[0], i[1]), i[2], 255, thickness=-1)
                masked_frame = cv2.bitwise_and(frame, frame, mask=mask)

                most_prominent_color_bgr = find_most_prominent_color(frame, (i[0], i[1]), i[2])
                ball_color = find_ball_color(most_prominent_color_bgr)
                cv2.circle(masked_frame, (i[0], i[1]), i[2], (0, 255, 0), 2)
                cv2.circle(masked_frame, (i[0], i[1]), 2, (0, 0, 255), 3)

            resized_frame = resize_image(masked_frame, scale_factor=0.5)
            cv2.imshow("Detected Circles with Prominent Colors", resized_frame)

        elif ball_in_frame:
            ball_in_frame = False
            exit_time = get_video_timestamp(frame_count, fps)
            # print("exit time: ", exit_time)
            entry_exit_times.append((entry_time, exit_time))

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Check if the ball is still in frame when the video ends
    if ball_in_frame:
        exit_time = get_video_timestamp(frame_count, fps)
        print("exit time: ", exit_time)
        entry_exit_times.append((entry_time, exit_time))

    cap.release()
    cv2.destroyAllWindows()

    # Write entry and exit times to a CSV file
    write_entry_exit_times_to_csv(quadrant, output_csv_path, entry_exit_times)

    return circle_coordinates

quad1 = r"quadrant1.avi"
quad2 = r"quadrant2.avi"
quad3 = r"quadrant3.avi"
quad4 = r"quadrant4.avi"

output_csv_path = "result.csv"
quad_1 = calculate_radius_video(1, quad1, output_csv_path)
quad_2 = calculate_radius_video(2, quad2, output_csv_path)
quad_3 = calculate_radius_video(3, quad3, output_csv_path)
quad_4 = calculate_radius_video(4, quad4, output_csv_path)
