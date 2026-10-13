// +build ignore
#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

struct osi_telemetry_t {
    __u32 layer; // 4 for Transport (TCP), 7 for Application (HTTP/gRPC)
    __u32 pid;
    __u32 tcp_flags;
    __u64 rtt_ns;
    char payload_snippet[32];
};

struct {
    __uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);
    __uint(max_entries, 4096);
} osi_events SEC(".maps");

// Layer 4 Transport Inspection: Track TCP Retransmits & Latency
SEC("kprobe/tcp_rcv_established")
int trace_transport_layer(struct pt_regs *ctx) {
    struct osi_telemetry_t event = {};
    event.layer = 4;
    event.pid = bpf_get_current_pid_tgid() >> 32;
    event.rtt_ns = bpf_ktime_get_ns();
    
    bpf_perf_event_output(ctx, &osi_events, BPF_F_CURRENT_CPU, &event, sizeof(event));
    return 0;
}

// Layer 7 Application Inspection: Intercept Socket Payload Writes for HTTP paths
SEC("kprobe/sys_enter_write")
int trace_application_layer(struct pt_regs *ctx) {
    struct osi_telemetry_t event = {};
    event.layer = 7;
    event.pid = bpf_get_current_pid_tgid() >> 32;
    
    bpf_perf_event_output(ctx, &osi_events, BPF_F_CURRENT_CPU, &event, sizeof(event));
    return 0;
}

char LICENSE[] SEC("license") = "GPL";