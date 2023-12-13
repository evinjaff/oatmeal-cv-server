
# Oatmeal CV Server

This contains the code for Group 7's Oatmeal CV server. The repo is divided into two folders `pi` and `server` that respectively contain client and server code.

## Server (server)

The server folder holds all the code needed to run the Flask server that displays the status and processes data sent from the client.

**NOTE:** If you want to run this on a Linux distribution in userspace, you may need to do some extra work. By default, Linux restricts the ability for Port 80 to be opened in userspace. If you have an SSL certificate, you can serve this on 443 over HTTPS. Alternatively, you can use the [authbind](https://manpages.ubuntu.com/manpages/xenial/man1/authbind.1.html) command which will let you bind your flask server to port 80. No such restriction exists on Windows or MacOS from my experience. You should also **ONLY** run on port 80 for testing as it is a **masssive security liability because your image is unencrypted**. For a production run, you should obtain an SSL certificate from [letsencrypt](https://letsencrypt.org/).

### Required packages/Virtual Environment

It is recommended to create a virtual environment server. In case one already exists type `sudo rm -rf venv/` inside the `server` folder and then run `python3 -m venv venv` to create a virtual environemnt. Activate this environment by typing `source venv/bin/activate`

We need a few additional packages to get things up and running. Run `pip install numpy opencv-python ultralytics flask` and then you should be ready for a script.

### Import pretrained weights

The server expects a `best.pt` file to live in the base `server` folder. We do not include one, because it violates GitHub's large file size rule. Either train you own weights using the training notebook under the training repo or get some pretrained weights elsewhere to do this.

### Deployment/Running as a service

While Flask can be run as a service, I would recommend actually using [tmux](https://tmuxcheatsheet.com/) or [GNU screen](https://www.gnu.org/software/screen/) to keep the full output available and be able to debug/interact with the server if needed. I personally used a persistent tmux session to keep track of things

## Client (pi)

The client code uploads the a photo from a USB-attached webcam to a service. If you want to use the raspberry pi camera module, it is unsupported. Use the [Raspberry Pi Imager](https://github.com/raspberrypi/rpi-imager) to image 64-bit Raspberry Pi OS to the SD card for the Pi.

### Required packages/Virtual Environment

It is recommended to create a virtual environment for the Pi (and required if you want to run it as a service). In case one already exists type `sudo rm -rf venv/` inside the `pi` folder and then run `python3 -m venv venv` to create a virtual environment. Activate this environment by typing `source venv/bin/activate`

In order to function on the client side, all that the Pi needs is the [requests for humans](https://requests.readthedocs.io/) and [opencv](https://pypi.org/project/opencv-python/) packages. Running `pip install requests opencv-python` should handle this dependency.

### Specifying Domain to Send Images to

Due to the class project nature, we haven't included command-line arguments to adjust the domain. For now, just edit `url` on line 39 to indicate the new site where things should get uploaded.

### Run it as a systemd service

It is highly recommended you run this script as a service, so that it will run whenever you turn the Pi on. Here is an example of what it should look like. You can create this file under `/etc/systemd/system/` and name it something like `oatmealcam.service`. You will need to point systemd to the python file inside your virtual environment like so:

```
[Unit]
Description=Oatmeal Pi Uploader
After=multi-user.target

[Service]
Type=idle
ExecStart=/path_to_this_repo/pi/venv/bin/python /path_to_this_repo/pi/uploader.py
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Enable the service by typing `sudo systemctl enable oatmealcam.service`

Start the service by typing `sudo systemctl start oatmealcam.service`

Check that it worked by typing `sudo systemctl status oatmealcam.service`

If you see 200s, on the log, then that means the pi is successfully uploading data.