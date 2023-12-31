import Levenshtein
import os
import sys
import matplotlib.pyplot as plt

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.characters_segmentator import segmentate_characters
from utils.plate_detector import find_plate


def show_image(image, title="Image"):
    plt.imshow(image, cmap="gray")
    plt.title(title)
    plt.show()


def check_error(actual_characters, predicted_full, predicted_segmented):
    """
    Helper function to calculate accuracy and print results for a single test case.

    Args:
        actual_characters (str): The actual characters in the image.
        predicted_full (str): Predicted characters from full plate.
        predicted_segmented (str): Predicted characters from segmented plate.

    Returns:
        accuracy_full_plate (float): Accuracy for full plate.
        accuracy_segmented_plate (float): Accuracy for segmented plate.
    """
    # Calculate Levenshtein distances for full plate and segmented plate
    if predicted_full:
        levenshtein_distance_full_plate = Levenshtein.distance(predicted_full, actual_characters)
        accuracy_full_plate = sum(1 for a, b in zip(predicted_full, actual_characters) if a == b) / len(actual_characters) * 100
    else:
        accuracy_full_plate = None
    levenshtein_distance_segmented_plate = Levenshtein.distance(predicted_segmented, actual_characters)

    # Calculate accuracy for full plate
    if predicted_full:
        accuracy_full_plate = sum(1 for a, b in zip(predicted_full, actual_characters) if a == b) / len(actual_characters) * 100

    # Calculate accuracy for segmented plate
    total_letters_correct = sum(1 for a, b in zip(predicted_segmented, actual_characters) if a == b)
    accuracy_segmented_plate = sum(1 for a, b in zip(predicted_segmented, actual_characters) if a == b) / len(actual_characters) * 100

    # Log results with Levenshtein distances
    print("\n--------------------")
    print(f'Actual characters: {actual_characters}')
    if predicted_full:
        print("\nFull plate:")
        print(f"\nPredicted:               {predicted_full}")
        print(f"Levenshtein distance:    {levenshtein_distance_full_plate} - {'Correct' if accuracy_full_plate == 100 else 'Incorrect'}")
        print(f"Accuracy:                {accuracy_full_plate:.2f}% - {'Correct' if accuracy_full_plate == 100 else 'Incorrect'}")
    print("\nSegmented plate:")
    print(f"\nPredicted:               {predicted_segmented}")
    print(f"Levenshtein distance:    {levenshtein_distance_segmented_plate} - {'Correct' if accuracy_segmented_plate == 100 else 'Incorrect'}")
    print(f"Accuracy:                {accuracy_segmented_plate:.2f}% - {'Correct' if accuracy_segmented_plate == 100 else 'Incorrect'}")

    if predicted_full:
        return accuracy_full_plate, accuracy_segmented_plate, total_letters_correct
    else:
        return 0, accuracy_segmented_plate, total_letters_correct


def validate_images(identify_character_funct, validate_with_full_plate=False, print_compare_img=False, model=None):
    """
    Function to test the identify_character function with the digits image files

    Args:
        img (string): image file path
    """

    total_img = 0
    total_letters_correct = 0
    total_correct_full_plate = 0
    total_correct_segmented_plate = 0

    img_directory = "../img/plates/"
    file_directory = os.path.dirname(os.path.realpath(__file__))

    predicted_full = None

    for test_img in os.listdir(os.path.join(file_directory, img_directory)):

        print("\n--------------------")
        print(f"Test image: {test_img}")

        actual_characters = test_img.split(".")[0]
        img_path = os.path.join(file_directory, img_directory + test_img)

        # Find plate
        plate, _ = find_plate(img_path)

        # Segmentate characters
        segmentated_chars = segmentate_characters("temp_plate.png")

        if validate_with_full_plate:
            # Predict characters in a segmented plate
            predicted_full = identify_character_funct(plate) if not model is None else identify_character_funct(plate, model)
            predicted_full = ''.join(e for e in predicted_full if e.isalnum())

        # Predict characters in a segmented plate
        predicted_segmentated = []
        for i, character in enumerate(segmentated_chars):
            try:
                character_result = identify_character_funct(character, False, i).strip() if not model else identify_character_funct(character, model).strip()
            except Exception:
                character_result = identify_character_funct(character).strip() if not model else identify_character_funct(character, model).strip()
            predicted_segmentated.append(''.join(e for e in character_result))

        predicted_segmentated = "".join(predicted_segmentated).replace(" ", "")

        # Call test_helper for accuracy calculation and logging
        accuracy_full_plate, accuracy_segmented_plate, total_letters_correct_seg = check_error(actual_characters, predicted_full, predicted_segmentated)

        if print_compare_img:
            show_image(plate, "Final")

        # Check if correct for full plate
        if accuracy_full_plate == 100:
            total_correct_full_plate += 1

        # Check if correct for segmented plate
        if accuracy_segmented_plate == 100:
            total_correct_segmented_plate += 1

        total_letters_correct += total_letters_correct_seg
        total_img += 1

    # Calculate overall accuracy percentages
    overall_percentage_accuracy_full_plate = (total_correct_full_plate / total_img) * 100
    overall_percentage_accuracy_segmented_plate = (total_correct_segmented_plate / total_img) * 100

    # Print overall test results
    print("\n--------------------")
    print(f"Total correct for full plate: {total_correct_full_plate} - {overall_percentage_accuracy_full_plate:.2f}%")
    print(f"Total correct for segmented plate: {total_correct_segmented_plate} - {overall_percentage_accuracy_segmented_plate:.2f}%")
    print(f"Total correct letters: {total_letters_correct} - {(total_letters_correct / (total_img * 7)) * 100:.2f}%")

    # Check overall test result based on overall accuracy percentages
    if overall_percentage_accuracy_full_plate >= 90 and overall_percentage_accuracy_segmented_plate >= 90:
        print("\n------------------ Test passed! ------------------")
        return True
    else:
        print("\n------------------ Test failed! ------------------")
        return False
