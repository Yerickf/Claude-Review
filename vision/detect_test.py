import argparse
import os
import time

import cv2


def list_cameras():
    print("A procurar câmaras 0-5...")
    for i in range(6):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW) if os.name == "nt" else cv2.VideoCapture(i)
        if cap.isOpened():
            ok, frame = cap.read()
            if ok:
                h, w = frame.shape[:2]
                print("  câmara %d: %dx%d" % (i, w, h))
        cap.release()
    print("Se a do telemóvel não aparece, abre primeiro a app (DroidCam/Camo/iVCam) e liga o cabo.")


def main():
    ap = argparse.ArgumentParser(description="Teste de deteção de marcadores (matriz de testes do G1)")
    ap.add_argument("--list", action="store_true", help="lista as câmaras disponíveis")
    ap.add_argument("--cam", type=int, default=0)
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=720)
    args = ap.parse_args()

    if args.list:
        list_cameras()
        return

    cap = cv2.VideoCapture(args.cam, cv2.CAP_DSHOW) if os.name == "nt" else cv2.VideoCapture(args.cam)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
    if not cap.isOpened():
        raise SystemExit("Não abri a câmara %d. Usa --list." % args.cam)

    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    params = cv2.aruco.DetectorParameters()
    params.cornerRefinementMethod = cv2.aruco.CORNER_REFINE_SUBPIX
    detector = cv2.aruco.ArucoDetector(dictionary, params)

    frames = 0
    hits = {}
    t0 = time.time()
    print("q = sair e mostrar a tabela | r = recomeçar a contagem | s = guardar frame")
    while True:
        ok, frame = cap.read()
        if not ok:
            continue
        frames += 1
        corners, ids, _ = detector.detectMarkers(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
        if ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)
            for i in ids.flatten():
                hits[int(i)] = hits.get(int(i), 0) + 1
        fps = frames / max(time.time() - t0, 1e-6)
        cv2.putText(frame, "fps %.0f  frames %d" % (fps, frames), (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        cv2.imshow("detect_test", frame)
        k = cv2.waitKey(1) & 0xFF
        if k == ord("q"):
            break
        if k == ord("r"):
            frames, hits, t0 = 0, {}, time.time()
        if k == ord("s"):
            name = "recordings/frame-%d.png" % int(time.time())
            cv2.imwrite(name, frame)
            print("guardado", name)

    cap.release()
    cv2.destroyAllWindows()
    print("\nID   frames com o ID   %% dos frames")
    for i in sorted(hits):
        print("%-4d %-17d %.1f%%" % (i, hits[i], 100.0 * hits[i] / max(frames, 1)))
    print("(G1: a peça parada tem de ter >= 98%% e nenhum ID que não esteja na mesa)")


if __name__ == "__main__":
    main()
