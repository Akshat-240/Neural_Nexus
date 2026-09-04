from ultralytics import YOLO


def main():
    model = YOLO("yolov8n.pt")
    results = model("test.jpg")

    for r in results:
        for box in r.boxes:
            name = model.names[int(box.cls[0])]
            confidence = float(box.conf[0])
            print(f"Found: {name} (confidence: {confidence:.2f})")

    results[0].save(filename="test_annotated.jpg")
    print("Done! Open test_annotated.jpg to see it")


if __name__ == "__main__":
    main()