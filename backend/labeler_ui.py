import streamlit as st
import pandas as pd
from PIL import Image
import os
import streamlit as st
from difflib import get_close_matches
import base64
from st_copy_to_clipboard import st_copy_to_clipboard   

st.set_page_config(layout="wide")

# Example function to provide suggestions
def suggest_phrases(input_text, phrase_list, max_suggestions=5):
    """
    Suggest corrections or completions for phrases.
    """
    return get_close_matches(input_text, phrase_list, n=max_suggestions, cutoff=0.2)

def render_image_with_selectable_text(image_path, words, bboxes):
    """
    Renders an image with an overlay of selectable text in Streamlit.

    Args:
        image_path (str): Path to the input image.
        words (list): List of words to overlay.
        bboxes (list): List of bounding boxes for each word in [x1, y1, x2, y2] format.
    """
    # Load the image
    image = Image.open(image_path)
    image_width, image_height = image.size

    # Encode the image to a base64 string for embedding in HTML
    with open(image_path, "rb") as img_file:
        image_base64 = base64.b64encode(img_file.read()).decode()

    # Create an HTML structure with selectable text overlay
    html_content = f"""
    <div style="position: relative; width: 100%; max-width: {image_width}px; margin: auto;">
        <img src="data:image/png;base64,{image_base64}" style="width: 100%; height: auto;" />
        <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%;">
    """

    for word, bbox in zip(words, bboxes):
        x1, y1, x2, y2 = bbox
        word_width = x2 - x1
        word_height = y2 - y1
        top = y1 / image_height * 100
        left = x1 / image_width * 100
        width = word_width / image_width * 100
        height = word_height / image_height * 100

        # Add a selectable word in the overlay
        html_content += f"""
        <div style="
            position: absolute;
            top: {top}%;
            left: {left}%;
            width: {width}%;
            height: {height}%;
            background-color: rgba(255, 255, 255, 0.5);
            color: black;
            font-size: 0.6vw;
            overflow: hidden;
            text-align: left;
            white-space: nowrap;
            pointer-events: auto;
        ">{word}
        </div>
        """

    html_content += "</div></div>"

    # Display the HTML in Streamlit
    st.html(html_content)


# Load data from CSV
@st.cache_data
def load_data(csv_path):
    return pd.read_csv(csv_path)

# Load image from file path
@st.cache_data
def load_image(image_path):
    return Image.open(image_path)

def format_radio(str):
    return ''

# Main UI
def main():
    st.title("Fine-Tuning Labeler (with PaddleOCR)")

    # Directories
    debug_images_dir = "debug_images"
    fine_tuning_dir = "fine_tuning"
    os.makedirs(fine_tuning_dir, exist_ok=True)

    # Get processed and unprocessed files
    corrected_files = [f.replace("_corrected.csv", "") for f in os.listdir(fine_tuning_dir) if f.endswith("_corrected.csv")]
    all_folders = [f for f in os.listdir(debug_images_dir) if os.path.isdir(os.path.join(debug_images_dir, f))]
    needs_review = [f for f in all_folders if f not in corrected_files]
    # Dropdown for file types
    file_types = [
        "1040_p1", "1040_sch_c", "1120S_p1", "1120S_bal_sheet", "1120S_k1",
        "1065_p1", "1065_bal_sheet", "1065_k1", "1120_p1", "1120_bal_sheet"
    ]
    top_col1, top_col2 = st.columns([1,0.5])
    # Apply file type filter

    with top_col1:
        selected_file_type = st.selectbox("Filter by file type:", ["ALL"] + file_types)
        
        # Toggle to filter folder list
        filter_option = st.radio("Filter folders by:", options=["ALL", "PROCESSED", "NEEDS_REVIEW"])
        if filter_option == "ALL":
            folders = all_folders
        elif filter_option == "PROCESSED":
            folders = corrected_files
        else:
            folders = needs_review

        if selected_file_type != "ALL":
            folders = [folder for folder in folders if selected_file_type in folder]

        selected_folder = st.selectbox("Select a folder to review:", folders)

    with top_col2:
        # Create a dictionary to count occurrences of each file type
        file_type_counts = {file_type: 0 for file_type in file_types}
        
        # Count file types in all folders
        for folder in os.listdir('fine_tuning'):
            for file_type in file_types:
                if file_type in folder:
                    file_type_counts[file_type] += 1

        # Convert the counts dictionary to a DataFrame
        file_type_df = pd.DataFrame(list(file_type_counts.items()), columns=["File Type", "Count"])
        
        # Display the DataFrame
        st.write("File Type Counts:")
        st.dataframe(file_type_df, hide_index=True)
        
    if selected_folder:
        folder_path = os.path.join(debug_images_dir, selected_folder)
        if selected_folder in corrected_files:
            csv_path = os.path.join(fine_tuning_dir, f"{selected_folder}_corrected.csv")
        else:
            csv_path = os.path.join(folder_path, "final_results.csv")

        if os.path.exists(csv_path):
            df = load_data(csv_path)
            # Add the single text input field for suggestions
            
            col0, col1 = st.columns([3,3])
            
            with col0:

                st.write("Original OCR Results:")
                with st.container(height=600):
                    c1, c2 = st.columns([1.5,0.15])
                    df_small = df[['key','question','answer']]
                    df_small['answer'] = df_small['answer'].astype(str) 
                    with c1:
                        edit_df = st.data_editor(
                            df_small, 
                            hide_index=True, 
                            height=1000)

                    with c2:
                        st.markdown("")
                        st.markdown(
                        """
                        <style>
                        .stRadio > div {
                            gap: 12px; /* Adjust this value for more or less spacing */
                        }
                        </style>
                        """,
                        unsafe_allow_html=True
                    )
                        selected_row = st.radio(label='Row',label_visibility='collapsed', format_func=format_radio, options=df['key'])

                # copy_row = st.selectbox("Copy words/bboxes from:", df['key'])

                # if st.button("Add Row"):
                #     wds = df.loc[df['key'] == copy_row, 'words'].values
                #     bb = df.loc[df['key'] == copy_row, 'bboxes'].values
                #     # st.text(wds)
                #     # st.text(bb)
                #     edit_df.add_row({"key": "", "question": "", "answer": "", "words":wds,"bboxes":bb})

                # Save corrected results
                if st.button("Save Corrections"):
                    df["question"] = edit_df['question']
                    df["answer"] = edit_df['answer']
                    save_path = os.path.join(fine_tuning_dir, f"{selected_folder}_corrected.csv")
                    df.to_csv(save_path, index=False)
                    st.success(f"Corrections saved to {save_path}")


            with col1:
                all_words = eval(df.loc[df['key'] == selected_row, "words"].values[0])
                # st.text(all_words)
                input_text = st.text_input("Type here to get suggestions:")
                if input_text:
                    # Provide suggestions based on input
                    suggestions = suggest_phrases(input_text, all_words)
                    if suggestions:
                        st.write("Suggestions:")
                        st.text(suggestions)
                        # for suggestion in suggestions:
                        #     st.write(f"- {suggestion}")
                    else:
                        st.write("No suggestions found.")
                # image = load_image(df.loc[df['key'] == selected_row, "image_path"].values[0])
                # st.image(image, caption="Image", use_column_width=True)
                # st.text_area("Word List:", value=df.loc[df['key'] == selected_row, "words"].values[0], disabled=True, height=400)
                img = df.loc[df['key'] == selected_row, "image_path"].values[0]
                ws = df.loc[df['key'] == selected_row, "words"].values[0]
                bb = df.loc[df['key'] == selected_row, "bboxes"].values[0]
                render_image_with_selectable_text(img, eval(ws), eval(bb))

        else:
            st.error(f"No `final_results.csv` found in {folder_path}.")

if __name__ == "__main__":
    main()
