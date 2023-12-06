import cv2

def divide_video_into_quadrants(input_video_path, output_paths):
    # Open the input video file
    cap = cv2.VideoCapture(input_video_path)

    # Get the video properties
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Validate the dimensions to be divisible by 2
    if width % 2 != 0 or height % 2 != 0:
        raise ValueError("Video dimensions must be divisible by 2 for quadrants division.")

    # Set the codec
    fourcc = cv2.VideoWriter_fourcc(*'XVID')

    # Create VideoWriter objects for each quadrant
    out_quadrants = [cv2.VideoWriter(output_path, fourcc, fps, (width // 2, height // 2))
                     for output_path in output_paths]

    # Read and write frames, dividing into quadrants
    while True:
        ret, frame = cap.read()
        if not ret:
            break  # Break the loop if the video ends

        # Divide the frame into four quadrants
        top_left = frame[:height // 2, :width // 2, :]
        top_right = frame[:height // 2, width // 2:, :]
        bottom_left = frame[height // 2:, :width // 2, :]
        bottom_right = frame[height // 2:, width // 2:, :]

        # Write each quadrant to the corresponding output file
        out_quadrants[2].write(top_left)
        out_quadrants[3].write(top_right)
        out_quadrants[1].write(bottom_left)
        out_quadrants[0].write(bottom_right)

    # Release the video capture and writer objects
    cap.release()
    for out in out_quadrants:
        out.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Specify input and output video paths
    input_path = "crop.avi"
    output_paths = ["quadrant1.avi", "quadrant2.avi", "quadrant3.avi", "quadrant4.avi"]

    # Divide the video into quadrants
    divide_video_into_quadrants(input_path, output_paths)
