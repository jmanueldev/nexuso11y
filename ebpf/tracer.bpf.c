// +build ignore
#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

struct http_event_t {
    __u32 pid;
    __u32 status_code;
    __u64 latency_ns;
    char path[64];
};

struct {
    __uint(type, BPF_MAP_TYPE_PERF_EVENT_ARRAY);
    __uint(max_entries, 256);
} nexus_events SEC(".maps");

SEC("kprobe/sys_enter_write")
int trace_write_entry(struct pt_regs *ctx) {
    __u32 pid = bpf_get_current_pid_tgid() >> 32;
    
    struct http_event_t event = {};
    event.pid = pid;
    event.latency_ns = bpf_ktime_get_ns();
    
    bpf_perf_event_output(ctx, &nexus_events, BPF_F_CURRENT_CPU, &event, sizeof(event));
    return 0;
}

char LICENSE[] SEC("license") = "GPL";