//Loading faceapi weights
const MODEL_URL = '/pos_face_recognition/static/src/js/weights';
import { _t } from "@web/core/l10n/translation";
import { SelectionPopup } from "@point_of_sale/app/utils/input_popups/selection_popup";
import { usePos } from "@point_of_sale/app/store/pos_hook";
import { patch } from "@web/core/utils/patch";
import { useService } from "@web/core/utils/hooks";
import { useRef, useState } from "@odoo/owl";
import { AlertDialog } from "@web/core/confirmation_dialog/confirmation_dialog";
faceapi.nets.ssdMobilenetv1.loadFromUri(MODEL_URL)
faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL)
faceapi.nets.faceRecognitionNet.loadFromUri(MODEL_URL)
faceapi.nets.tinyFaceDetector.load(MODEL_URL),
faceapi.nets.faceLandmark68TinyNet.load(MODEL_URL),
faceapi.nets.faceExpressionNet.load(MODEL_URL),
faceapi.nets.ageGenderNet.load(MODEL_URL)
//Patching SelectionPopup component to add face login system
patch(SelectionPopup.prototype, {
    setup() {

        super.setup(...arguments);
        this.pos = usePos();
        this.rootRef = useRef("root");
        this.rootEmp = useRef("rootEmp");
        this.dialog = useService("dialog");
        this.faceMatcher = null;
    },
//    Function which will decide to open the web camera
    async selectItem(itemId) {
        this.state.selectedId = itemId;
        await this.loadImage(itemId)
        if (this.have_image != false) {
            await this.startWebcam()
        } else {
        this.dialog.add(AlertDialog, {
                title: _t("Authentication failed"),
                body: _t(
                    "Selected cashier have no image.."
                ),
            });
        }
    },

//    Function which will load the cashier image
    async loadImage(itemId){
        const user = this.pos.models["hr.employee"].find(
                    (emp) => emp.id === itemId
                );
        this.have_image = user.image
        const employee_image = this.rootEmp.el
        if (this.have_image != false) {
            employee_image.src = "data:image/jpeg;base64," + user.image
        }
    },

//    Function to start the web camera
    startWebcam(){
        const video = document.getElementById('video')
        navigator?.mediaDevices.getUserMedia(
        { video: true, audio: false }
        ).then((stream) => {
            video.srcObject = stream
        }).catch((error) => {
            console.error(error)
        }).then(this.faceRecognition(video))
    },

//    Function to get the descriptions of cashier image
    async getLabeledFaceDescriptions(){
        const employee_image = this.rootEmp.el;
        const detections = await faceapi
                    .detectSingleFace(employee_image)
                    .withFaceLandmarks()
                    .withFaceExpressions()
                    .withFaceDescriptor();
        return detections
    },

//    Function which compares the webcam image with cashier image
    async faceRecognition(video){
        const labeledFaceDescriptors = await this.getLabeledFaceDescriptions()
        if (!this.faceMatcher) {
            this.faceMatcher = new faceapi.FaceMatcher([labeledFaceDescriptors.descriptor]);
        }
        video.addEventListener('play', () => {
            const canvas = faceapi.createCanvasFromMedia(video);
            document.body.append(canvas);
            const displaySize = {width: video.width, height: video.height}
            faceapi.matchDimensions(canvas, displaySize)
            setInterval(async () => {
                const detections = await faceapi
                    .detectAllFaces(video)
                    .withFaceLandmarks()
                    .withFaceExpressions()
                    .withFaceDescriptors();
                    detections.forEach((detection) => {
                    const match = this.faceMatcher.findBestMatch(detection.descriptor);
                    if (match._distance < 0.4  ) { // Adjust threshold as needed
                        const modal = this.rootRef.el;
                        if (modal) {
                            modal.style.display = 'none';
                            this.modalVisible = false;
                            this.confirm();
                            video.srcObject.getTracks().forEach(track => track.stop());
                            canvas.remove();
                        }
                    }
                    else {
                        this.dialog.add(AlertDialog, {
                        title: _t("Authentication failed"),
                        body: _t(
                            "Face not recognized.."
                            ),
                        });
                        location.reload();
                    }
                });
            }, 100);
        })
    },
})