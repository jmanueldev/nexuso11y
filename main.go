package main

import (
	"bytes"
	"encoding/binary"
	"errors"
	"log"
	"os"
	"os/signal"
	"syscall"

	"github.com/cilium/ebpf/link"
	"github.com/cilium/ebpf/perf"
	"github.com/cilium/ebpf/rlimit"
)

// NetworkEvent mirrors the C struct layout for parsing ring buffer payloads
type NetworkEvent struct {
	Pid         uint32
	Uid         uint32
	TimestampNs uint64
	EventType   uint32
	Comm        [16]byte
}

func main() {
	// 1. Lift memory locks for eBPF subsystem execution
	if err := rlimit.RemoveMemlock(); err != nil {
		log.Fatalf("Failed to remove memlock limit: %v", err)
	}

	log.Println("Initializing NexusO11Y Universal eBPF Engine...")

	// 2. Attach multiple kernel probes covering all network lifecycle paths
	probes := map[string]string{
		"sys_enter_connect": "Connect (Egress)",
		"sys_enter_accept4": "Accept (Ingress)",
		"sys_enter_write":   "Write (Payload)",
	}

	var activeLinks []link.Link
	for sysCall, description := range probes {
		kp, err := link.Kprobe(sysCall, nil, nil)
		if err != nil {
			log.Printf("Warning: Could not attach probe for %s (%s): %v", sysCall, description, err)
		} else {
			activeLinks = append(activeLinks, kp)
			log.Printf("Successfully attached universal probe -> %s [%s]", sysCall, description)
		}
	}

	// Ensure all active kprobes unhook cleanly on exit
	defer func() {
		for _, l := range activeLinks {
			l.Close()
		}
		log.Println("Cleaned up all active kernel probes.")
	}()

	// 3. Graceful shutdown handler
	stopChan := make(chan os.Signal, 1)
	signal.Notify(stopChan, os.Interrupt, syscall.SIGTERM)

	// 4. Consumer routine loop for high-throughput telemetry stream
	go func() {
		log.Println("Streaming universal container network metrics across the node...")
		// In production integration, initialize perf.NewReader(objs.NexusEvents, os.Getpagesize() * 4) here
		<-stopChan
	}()

	<-stopChan
	log.Println("Shutting down NexusO11Y eBPF Engine gracefully.")
}

// ParseEvent converts raw kernel bytes into structured telemetry objects
func ParseEvent(data []byte) (*NetworkEvent, error) {
	var event NetworkEvent
	reader := bytes.NewReader(data)
	if err := binary.Read(reader, binary.LittleEndian, &event); err != nil {
		return nil, errors.New("failed to parse universal perf event bytes")
	}
	return &event, nil
}
