# Cloud Storage Setup Guide

This guide provides instructions on how to set up cloud storage for your landslide monitoring system. Storing your captured images in the cloud ensures data redundancy, accessibility from anywhere, and easy sharing.

## 1. Choose a Cloud Provider

The landslide monitoring system is designed to be flexible and can integrate with various cloud storage providers. Popular choices include:

*   **Amazon S3 (AWS Simple Storage Service):** A highly scalable, durable, and secure object storage service. Ideal for long-term storage and integration with other AWS services.
*   **Google Drive:** A user-friendly cloud storage service that offers generous free storage and easy integration with Google's ecosystem.
*   **SFTP (SSH File Transfer Protocol) Server:** A secure way to transfer files over SSH. You can set up your own SFTP server or use a hosted solution.

Choose the provider that best suits your needs in terms of cost, features, and ease of use.

## 2. Set Up Cloud Credentials

Before configuring your landslide monitoring system, you need to obtain the necessary credentials from your chosen cloud provider.

### Amazon S3

1.  **Create an AWS Account:** If you don't have one, sign up for an AWS account at [aws.amazon.com](https://aws.amazon.com/).
2.  **Create an S3 Bucket:** In the AWS Management Console, navigate to S3 and create a new bucket. Choose a unique name and a region close to your deployment location.
3.  **Create an IAM User:** Go to IAM (Identity and Access Management) and create a new user. Grant this user programmatic access (Access key - Programmatic access).
4.  **Attach Policies:** Attach policies that grant the user permissions to access your S3 bucket. The `AmazonS3FullAccess` policy is sufficient for testing, but for production, it's recommended to create a custom policy with more restrictive permissions (e.g., `s3:PutObject`, `s3:GetObject`, `s3:DeleteObject` for your specific bucket).
5.  **Obtain Access Keys:** After creating the user, you will be provided with an Access Key ID and a Secret Access Key. **Save these securely**, as they will not be shown again.

### Google Drive

1.  **Create a Google Cloud Project:** Go to the Google Cloud Console at [console.cloud.google.com](https://console.cloud.google.com/) and create a new project.
2.  **Enable Google Drive API:** In your project, navigate to 


the "APIs & Services" -> "Library" and search for "Google Drive API" and enable it.
3.  **Create Service Account Credentials:** Go to "APIs & Services" -> "Credentials". Click "Create Credentials" -> "Service Account". Follow the steps to create a service account. Note down the service account email address.
4.  **Grant Folder Access:** In your Google Drive, create a folder where you want to store the images. Share this folder with the service account email address you just created (grant "Editor" access).
5.  **Download JSON Key File:** After creating the service account, click on it, then go to "Keys" -> "Add Key" -> "Create new key" -> "JSON". Download this JSON file. **Keep this file secure.**

### SFTP Server

1.  **Set up an SFTP Server:** You can use an existing SFTP server or set up your own. Ensure it is accessible from your Raspberry Pi.
2.  **Create a User Account:** Create a dedicated user account on your SFTP server for the Raspberry Pi. This account should have write permissions to the directory where you want to store the images.
3.  **Obtain Credentials:** Note down the SFTP server hostname/IP address, port (default is 22), username, and password. For enhanced security, consider using SSH key-based authentication instead of passwords.
    *   **SSH Key-based Authentication:** Generate an SSH key pair on your Raspberry Pi (if you haven't already) using `ssh-keygen`. Copy the public key to your SFTP server's `~/.ssh/authorized_keys` file for the SFTP user.

## 3. Configure the Landslide Monitoring System

Once you have your cloud credentials, you need to update the `config.json` file in your `landslide_monitoring` project to include these details.

1.  **Locate `config.json`:** This file is typically located in the root directory of your `landslide_monitoring` project.
2.  **Edit `config.json`:** Open the `config.json` file using a text editor. You will find a section for `cloud_storage`.

    ```json
    {
        "cloud_storage": {
            "provider": "",
            "aws_s3": {
                "access_key_id": "",
                "secret_access_key": "",
                "bucket_name": "",
                "region": ""
            },
            "google_drive": {
                "service_account_file": "/path/to/your/service_account.json",
                "folder_id": ""
            },
            "sftp": {
                "host": "",
                "port": 22,
                "username": "",
                "password": "",
                "remote_path": "/path/on/sftp/server",
                "ssh_key_path": "/path/to/your/ssh_key"
            },
            "upload_interval_minutes": 60
        }
    }
    ```

3.  **Fill in Your Details:**

    *   **`provider`**: Set this to `

aws_s3`, `google_drive`, or `sftp` based on your chosen provider.

    *   **For Amazon S3:** Fill in `access_key_id`, `secret_access_key`, `bucket_name`, and `region`.
    *   **For Google Drive:** Provide the absolute `path` to your downloaded service account JSON file and the `folder_id` of your shared Google Drive folder. The `folder_id` can be found in the URL of the Google Drive folder (e.g., `https://drive.google.com/drive/folders/YOUR_FOLDER_ID`).
    *   **For SFTP:** Fill in `host`, `port`, `username`, `password` (if not using SSH keys), `remote_path`, and optionally `ssh_key_path` if using SSH key-based authentication.

    *   **`upload_interval_minutes`**: Define how often the system should attempt to upload captured images to the cloud.

## 4. Test Cloud Integration

After configuring `config.json`, it is crucial to test the cloud integration to ensure everything is working correctly.

1.  **Run the Scheduler with Cloud Upload:**
    Navigate to the `landslide_monitoring` directory in your Raspberry Pi terminal and activate the virtual environment:
    ```bash
    cd /home/ubuntu/landslide_monitoring
    source venv/bin/activate
    ```
    Then, run the scheduler with the cloud upload option. This will trigger an immediate upload attempt.
    ```bash
    python3 core/scheduler.py --upload-cloud
    ```
2.  **Check Cloud Storage:** Log in to your chosen cloud storage provider (AWS S3 console, Google Drive, or SFTP client) and verify that the test images have been uploaded successfully.
3.  **Review Logs:** Check the system logs for any errors related to cloud uploads. The logs will provide detailed information if there are any issues with authentication or connectivity.

    ```bash
    tail -f logs/system.log
    ```

By following these steps, you can successfully set up and configure cloud storage for your landslide monitoring system, ensuring your valuable image data is securely backed up and accessible remotely.

