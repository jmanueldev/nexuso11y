// +build ignore
#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>
#include <bpf/bpf_core_read.h>

#define TASK_COMM_LEN 16

// Unified event schema sent from kernel space to user space
struct network_event_t {
    __u32 pid;
    __u32 uid;
    __u64 timestamp_ns;
    __u32 event_type; // 1: Connect (Egress), 2: Accept (Ingress), 3: Write (Payload/RED)
    char comm[TASK_COMM_LEN];
};

struct {
    __uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);
    __uint(max_entries, 2048);
} nexus_events SEC(".maps");

// 1. Intercept all outbound network connections (Egress traffic & API calls)
SEC("kprobe/sys_enter_connect")
int trace_connect_enter(struct pt_regs *ctx) {
    struct network_event_t event = {};
    event.pid = bpf_get_current_pid_tgid() >> 32;
    event.uid = bpf_get_current_uid_gid();
    event.timestamp_ns = bpf_ktime_get_ns();
    event.event_type = 1; // Connect
    bpf_get_current_comm(&event.comm, sizeof(event.comm));

    bpf_perf_event_output(ctx, &nexus_events, BPF_F_CURRENT_CPU, &event, sizeof(event));
    return 0;
}

// 2. Intercept inbound connections (Incoming API gateway traffic)
SEC("kprobe/sys_enter_accept4")
int trace_accept_enter(struct pt_regs *ctx) {
    struct network_event_t event = {};
    event.pid = bpf_get_current_pid_tgid() >> 32;
    event.uid = bpf_get_current_uid_gid();
    event.timestamp_ns = bpf_ktime_get_ns();
    event.event_type = 2; // Accept
    bpf_get_current_comm(&event.comm, sizeof(event.comm));

    bpf_perf_event_output(ctx, &nexus_events, BPF_F_CURRENT_CPU, &event, sizeof(event));
    return 0;
}

// 3. Intercept data packet writes (RED metric calculations - Rate, Errors, Duration)
SEC("kprobe/sys_enter_write")
int trace_write_enter(struct pt_regs *ctx) {
    struct network_event_t event = {};
    event.pid = bpf_get_current_pid_tgid() >> 32;
    event.uid = bpf_get_current_uid_gid();
    event.timestamp_ns = bpf_ktime_get_ns();
    event.event_type = 3; // Write
    bpf_get_current_comm(&event.comm, sizeof(event.comm));

    bpf_perf_event_output(ctx, &nexus_events, BPF_F_CURRENT_CPU, &event, sizeof(event));
    return 0;
}

char LICENSE[] SEC("license") = "GPL";
