import boto3
from tkinter import *
from tkinter import filedialog 
import os

############################################Global Variables##################################################
s3_client = boto3.client('s3')
bucket_name = ""
upload_file_location = ""
upload_file_name = ""
download_dir = os.path.join(os.path.expanduser('~'), 'downloads')
###############################################################################################################



############################################Functions##########################################################

#
#
#   Function used to set the name of the bucket which images will be uploaded/downloaded to and from
#
#
def getBucketName():
    global bucket_name
    bucket_name = bucket_name_entry.get()
    bucket_name_confirm.configure(text="Bucket name: " + bucket_name)

#
#
#   Function used to retrieve the available images which can be downloaded from the bucket
#
#   @Params
#   String bucketName =  The name of the bucket where the objects shall be retrieved from
#
def getBucketContents(bucketName):
    keys = []
    resp = s3_client.list_objects(Bucket=bucketName)
    for o in resp['Contents']:
        keys.append(o['Key'])
    return keys

#
#
#   Function called when the 'upload image' button is clicked. If the bucket name has been specified, a file explorer window is opened
#   and the user may select an image to upload. If no name is specified, a warning popup is called alerting the user to enter a 
#   bucket name.
#
def upload(): 
    if bucket_name != "":
        filename = filedialog.askopenfilename(initialdir = "/", title = "Select a File", 
                                                filetypes = [("Image files", ".jpg .jpeg .png .gif"), ("all files", "*.*")]) 
        global upload_file_location
        upload_file_location = filename
        last_dash = filename.rfind('/') + 1
        last_char = len(filename)
        global upload_file_name 
        upload_file_name = filename[last_dash:last_char]

        dl_ul_label.configure(text="Chosen file: "+upload_file_name) 
        confirm_upload() ## Calls a popup box prompting the user with an 'are you sure?' message.
    else:
        error = Toplevel()
        error.geometry("250x250")
        error.wm_title("No bucket name entered!")
        error_label = Label(error, text="Please enter a bucket name before uploading.")
        error_label.grid(column = 0, row = 0)
        error_button = Button(error, text="Ok", command=error.destroy)
        error_button.grid(column = 0, row = 1)


#
#
#   Function which prompts the user with an 'are you sure?' message for the image the user is trying to upload.
#
#
def confirm_upload():
    popup = Toplevel()
    popup.geometry("250x250")
    popup.wm_title("Confirm Upload")
    confirm_label = Label(popup, text="Are you sure you want to upload " + upload_file_name + "?")
    confirm_label.grid(column = 0, row = 0)
    confirm_button = Button(popup, text="Ok", command=lambda: [s3_send_file(), popup.destroy()]) ## Uploads the file to the S3 bucket
    confirm_button.grid(column = 0, row = 1)
    cancel_button = Button(popup, text="Cancel", command=popup.destroy) ## Cancels the action and closes the window
    cancel_button.grid(column = 0, row = 2)

#
#
#   Function which uploads the file which has been selected to the S3 bucket
#
#
def s3_send_file():
    s3_client.upload_file(upload_file_location, bucket_name, upload_file_name)

#
#
#   Function which is called when the 'download image' button is clicked by the user. If the bucket name is defined, the user is
#   presented with a list of images from the S3 bucket which they are free to download. If the bucket name is not defined then a
#   warning popup window is called which alerts the user that they have not specified a bucket to download from. 
#
#
def download():
    if bucket_name != "":
        keys = getBucketContents(bucket_name)
        popup = Toplevel()
        popup.geometry("250x250")
        popup.wm_title("Choose image to download")
        download_label = Label(popup, text="Please choose which image you wish to download")
        download_label.grid(column = 0, row = 0)
        var = StringVar(popup)
        var.set(keys[0])
        download_list = OptionMenu(popup, var, *keys)
        download_list.grid(column = 0, row = 1)
        download_button = Button(popup, text = "Download", command=lambda:[download_image(var.get()), popup.destroy()]) ##  Downloads the selected image
        download_button.grid(column = 0, row = 2)
    else:
        error = Toplevel()
        error.geometry("250x250")
        error.wm_title("No bucket name entered!")
        error_label = Label(error, text="Please enter a bucket name before downloading.")
        error_label.grid(column = 0, row = 0)
        error_button = Button(error, text="Ok", command=error.destroy)
        error_button.grid(column = 0, row = 1)

#
#
#   Function which downloads the selected image from the S3 bucket to the download directory.
#
#
def download_image(image_dl):
    s3_client.download_file(bucket_name, image_dl, download_dir+'/'+image_dl)


#############################################################################################################



#################################################Script######################################################
##  Defines and sets the windows, labels and buttons which are mapped to their appropriate functions. 

window = Tk() 
    
window.title('Upload or Download Images to S3') 
   
window.geometry("500x500") 

window.config(background = "white") 

bucket_name_lbl = Label(window, text="Please enter the bucket name below:", width =75, height = 5, fg = "black")

bucket_name_entry = Entry(window, bd = 5)

dl_ul_label = Label(window, text = "Please choose an option", width = 75, height = 5, fg = "black") 
       
button_upload = Button(window, text = "Upload Image", command = upload)  

button_download = Button(window, text= "Download Image", command = download)

button_set_bucket = Button(window, text="Set Bucket Name", command = getBucketName)

bucket_name_confirm = Label(window, text="", width = 75, height = 5, fg = "black")

bucket_name_lbl.grid(column = 1, row = 1)

bucket_name_entry.grid(column = 1, row = 2)

button_set_bucket.grid(column = 1, row = 3)

bucket_name_confirm.grid(column = 1, row = 4)

dl_ul_label.grid(column = 1, row = 5) 
   
button_upload.grid(column = 1, row = 6) 

button_download.grid(column = 1, row = 7)
   
window.mainloop()


###################################################################################################################
