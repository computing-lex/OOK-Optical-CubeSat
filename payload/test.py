import time
import argparse
import random

def simulate_frame_transfer(data_rate, total_frames, tx_error_power, rx_error_power):
    print(" Starting SFP Data Stream Simulation")
    print(f" Data Rate: {data_rate} Mbps")
    print(f" Total Frames to Send: {total_frames}")
    print(f" Tx Error Power: {tx_error_power} dBm")
    print(f" Rx Error Power: {rx_error_power} dBm\n")

    frames_sent = 0
    frames_received = 0
    errors = 0

    interval = 1 / (data_rate * 1e6 / (8 * 1024))  # assuming 1 frame = 1024 bytes

    for frame_id in range(1, total_frames + 1):
        time.sleep(interval)

        # Simulate transmission with random error based on error power
        tx_success = random.random() > tx_error_power
        rx_success = random.random() > rx_error_power

        if tx_success and rx_success:
            frames_received += 1
            status = "Success"
        else:
            errors += 1
            status = "Error"

        frames_sent += 1

        print(f"Frame {frame_id:04d}: Sent | Received: {frames_received:04d} | Errors: {errors:03d} | Status: {status}")

    print("\n📊 Simulation Complete")
    print(f"📤 Total Sent:     {frames_sent}")
    print(f"📥 Total Received: {frames_received}")
    print(f"❗ Errors:          {errors}")
    print("🔚 Exiting...\n")

def main():
    parser = argparse.ArgumentParser(description="SFP to SFP Data Stream Simulator")
    parser.add_argument("--data-rate", type=float, default=100, help="Data rate in Mbps")
    parser.add_argument("--frames", type=int, default=50, help="Number of frames to transmit")
    parser.add_argument("--tx-error", type=float, default=0.01, help="Tx error power probability (0.0 to 1.0)")
    parser.add_argument("--rx-error", type=float, default=0.01, help="Rx error power probability (0.0 to 1.0)")
    
    args = parser.parse_args()

    simulate_frame_transfer(
        data_rate=args.data_rate,
        total_frames=args.frames,
        tx_error_power=args.tx_error,
        rx_error_power=args.rx_error
    )

if __name__ == "__main__":
    main()
