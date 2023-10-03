#!pip install opencv-python==3.4.13.47
import streamlit as st
import os
st.sidebar.header("Admin Portal")
id = st.sidebar.text_input("Enter Login Id: ")
password = hash(st.sidebar.text_input("Enter Password",type="password"))
true_password = hash("PassFile@2023#")
if(id and password):
    if(password == true_password):
        st.sidebar.success("Successfully loggged in as admin")
        with st.expander("ADMIN PORTAL"):
            size = 0
            for items in os.listdir():
                file_size = os.stat(items).st_size / (1024 * 1024)
                size += file_size
            if(800 - size < 200):
                st.error(str(round(800 - size,2)) + " MB/800 MB")
            elif (800 - size > 200 and 800 - size < 600):
                st.warning(str(round(800 - size,2)) + " MB/800 MB")
            elif (800 - size > 600):
                st.success(str(round(800 - size,2)) + " MB/800 MB")
            file_uploads = st.file_uploader("Upload your file",accept_multiple_files=True)
            if file_uploads:
                for upload in file_uploads:
                    with open(upload.name, "wb") as f:
                        f.write(upload.read())
                st.success("uploaded successfully!")
            files = ["--select--"]
            show_files = ["--select--"]
            for items in os.listdir(os.getcwd()):
                if (".idea" in items):
                    pass
                elif ("requirements.txt" in items):
                    pass
                elif ("packages.txt" in items):
                    pass
                elif ("FileFormatChanger_Major.py" in items):
                    pass
                elif ("FileFormatChanger_Major - OlderVersion backup.py" in items):
                    pass
                elif (".git" in items):
                    pass
                elif (".streamlit" in items):
                    pass
                else:
                    files.append(items)
                    show_files.append(items + " " + str(round(os.stat(items).st_size / (1024*1024),2)) + " MB")
            sec = st.selectbox("Choose the file you want to delete: ",show_files)
            if(sec != "--select--"):
                os.remove(files[show_files.index(sec)])
                st.success("Successfully deleted " + sec)
    else:
        st.sidebar.error("Incorrect id/password")

