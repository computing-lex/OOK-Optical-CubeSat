#include <linux/module.h>
#define INCLUDE_VERMAGIC
#include <linux/build-salt.h>
#include <linux/elfnote-lto.h>
#include <linux/vermagic.h>
#include <linux/compiler.h>

BUILD_SALT;
BUILD_LTO_INFO;

MODULE_INFO(vermagic, VERMAGIC_STRING);
MODULE_INFO(name, KBUILD_MODNAME);

__visible struct module __this_module
__section(".gnu.linkonce.this_module") = {
	.name = KBUILD_MODNAME,
	.init = init_module,
#ifdef CONFIG_MODULE_UNLOAD
	.exit = cleanup_module,
#endif
	.arch = MODULE_ARCH_INIT,
};

#ifdef CONFIG_RETPOLINE
MODULE_INFO(retpoline, "Y");
#endif

static const struct modversion_info ____versions[]
__used __section("__versions") = {
	{ 0x25f8bfc1, "module_layout" },
	{ 0x609f1c7e, "synchronize_net" },
	{ 0x2d3385d3, "system_wq" },
	{ 0x9b6073e2, "device_remove_file" },
	{ 0x745fbadf, "netdev_info" },
	{ 0xc1c7e6c0, "kmalloc_caches" },
	{ 0x127f1a78, "pci_write_config_dword" },
	{ 0xeb233a45, "__kmalloc" },
	{ 0xc4f0da12, "ktime_get_with_offset" },
	{ 0xf9a482f9, "msleep" },
	{ 0x862258db, "timecounter_init" },
	{ 0x1fdc7df2, "_mcount" },
	{ 0xed6b80f3, "pci_enable_sriov" },
	{ 0xabcec5a0, "hwmon_device_register_with_groups" },
	{ 0xb5b54b34, "_raw_spin_unlock" },
	{ 0xb6320627, "pci_write_config_word" },
	{ 0xd6ee688f, "vmalloc" },
	{ 0xf1da5aaa, "param_ops_int" },
	{ 0x91eb9b4, "round_jiffies" },
	{ 0x28ef4c7f, "napi_disable" },
	{ 0x98cf60b3, "strlen" },
	{ 0x7c1e49b1, "pci_read_config_byte" },
	{ 0x970f20a5, "napi_schedule_prep" },
	{ 0x8f996a30, "ethtool_convert_legacy_u32_to_link_mode" },
	{ 0x41ed3709, "get_random_bytes" },
	{ 0x39513822, "dma_set_mask" },
	{ 0xe6de45a, "dev_mc_add_excl" },
	{ 0x5821f3a1, "pci_disable_device" },
	{ 0x6b683ab2, "dev_uc_add_excl" },
	{ 0xc7a4fbed, "rtnl_lock" },
	{ 0xeb1c4eaa, "pci_disable_msix" },
	{ 0x1bfaf7b, "hwmon_device_unregister" },
	{ 0x4ea25709, "dql_reset" },
	{ 0x95855422, "netif_carrier_on" },
	{ 0x12a4e128, "__arch_copy_from_user" },
	{ 0x2fde57c0, "pci_disable_sriov" },
	{ 0xffeedf6a, "delayed_work_timer_fn" },
	{ 0x402c5a08, "netif_carrier_off" },
	{ 0x56470118, "__warn_printk" },
	{ 0x3c12dfe, "cancel_work_sync" },
	{ 0x827a80ca, "alloc_pages" },
	{ 0x9a08e796, "__dev_kfree_skb_any" },
	{ 0xeae3dfd6, "__const_udelay" },
	{ 0xc6f46339, "init_timer_key" },
	{ 0x9fa7184a, "cancel_delayed_work_sync" },
	{ 0x3182c78f, "__pm_runtime_resume" },
	{ 0xb8a1d410, "pci_enable_wake" },
	{ 0x999e8297, "vfree" },
	{ 0xdf204797, "dma_free_attrs" },
	{ 0xbaf22757, "kvfree_call_rcu" },
	{ 0x3c3ff9fd, "sprintf" },
	{ 0x18aac8af, "dma_set_coherent_mask" },
	{ 0x15ba50a6, "jiffies" },
	{ 0xe6cd06c7, "__netdev_alloc_skb" },
	{ 0x807e5815, "__pskb_pull_tail" },
	{ 0xf1be6063, "ptp_clock_unregister" },
	{ 0x80c0af65, "pci_set_master" },
	{ 0x1eac1b0, "netif_schedule_queue" },
	{ 0xd85c5e47, "_dev_warn" },
	{ 0xdcb764ad, "memset" },
	{ 0x984ccc2a, "pci_enable_pcie_error_reporting" },
	{ 0xdfc9c3d7, "dma_sync_single_for_cpu" },
	{ 0x1e1e140e, "ns_to_timespec64" },
	{ 0x34a0c653, "netif_tx_wake_queue" },
	{ 0x2ad90978, "pci_restore_state" },
	{ 0x4b0a3f52, "gic_nonsecure_priorities" },
	{ 0x9f91bcf2, "netif_tx_stop_all_queues" },
	{ 0xd35cce70, "_raw_spin_unlock_irqrestore" },
	{ 0xa50a3da7, "_find_next_bit" },
	{ 0xbe7492b9, "pci_aer_clear_nonfatal_status" },
	{ 0xa00aca2a, "dql_completed" },
	{ 0xcd279169, "nla_find" },
	{ 0xb6568815, "free_netdev" },
	{ 0x42c4eece, "register_netdev" },
	{ 0x365acda7, "set_normalized_timespec64" },
	{ 0xa5e16cdd, "napi_enable" },
	{ 0xd9ad613, "pci_read_config_word" },
	{ 0x8ec7dbb2, "dma_alloc_attrs" },
	{ 0x20f3c878, "dev_close" },
	{ 0xf83251ef, "kfree_skb_reason" },
	{ 0xa7a2e932, "netif_set_real_num_rx_queues" },
	{ 0xc38c83b8, "mod_timer" },
	{ 0xe2504c9c, "netif_set_real_num_tx_queues" },
	{ 0x18cf4aed, "netif_napi_add" },
	{ 0x68dab42e, "ptp_clock_register" },
	{ 0x92d5838e, "request_threaded_irq" },
	{ 0x474f9680, "skb_pull" },
	{ 0x6b4b2933, "__ioremap" },
	{ 0x89c9a638, "_dev_err" },
	{ 0x18a235d6, "pci_enable_msi" },
	{ 0x42160169, "flush_workqueue" },
	{ 0xe523ad75, "synchronize_irq" },
	{ 0x6f9e763b, "timecounter_read" },
	{ 0x17692f0f, "pci_find_capability" },
	{ 0x48d56dfd, "device_create_file" },
	{ 0x360265e6, "eth_get_headlen" },
	{ 0x985bf7c3, "pci_select_bars" },
	{ 0x55e31703, "ethtool_convert_link_mode_to_legacy_u32" },
	{ 0xc6cbbc89, "capable" },
	{ 0xbc3f2cb0, "timecounter_cyc2time" },
	{ 0x6bf0bba5, "netif_device_attach" },
	{ 0xea2fe981, "napi_gro_receive" },
	{ 0x85fd2dbe, "_dev_info" },
	{ 0x40a9b349, "vzalloc" },
	{ 0xbdb821cb, "__free_pages" },
	{ 0x618911fc, "numa_node" },
	{ 0x8c676699, "netif_device_detach" },
	{ 0x1e1fc5ad, "__alloc_skb" },
	{ 0xa916b694, "strnlen" },
	{ 0xe77bf8a, "pci_enable_msix_range" },
	{ 0xa748901f, "__napi_schedule" },
	{ 0x6cbbfc54, "__arch_copy_to_user" },
	{ 0xb2fcb56d, "queue_delayed_work_on" },
	{ 0x296695f, "refcount_warn_saturate" },
	{ 0x3ea1b6e4, "__stack_chk_fail" },
	{ 0xac5ebbd0, "pm_schedule_suspend" },
	{ 0x92997ed8, "_printk" },
	{ 0x908e5601, "cpu_hwcaps" },
	{ 0xf9236d43, "napi_complete_done" },
	{ 0xf360d110, "dma_map_page_attrs" },
	{ 0xd9077296, "pci_read_config_dword" },
	{ 0x9f0b2287, "eth_type_trans" },
	{ 0x69f38847, "cpu_hwcap_keys" },
	{ 0xf38a2402, "dev_driver_string" },
	{ 0xd89d96d0, "pskb_expand_head" },
	{ 0x57a14207, "netdev_err" },
	{ 0xcbd4898c, "fortify_panic" },
	{ 0xd1ba9b3c, "pci_unregister_driver" },
	{ 0xcc5005fe, "msleep_interruptible" },
	{ 0xd58d4b67, "kmem_cache_alloc_trace" },
	{ 0xba8fbd64, "_raw_spin_lock" },
	{ 0x34db050b, "_raw_spin_lock_irqsave" },
	{ 0x32d1a1e5, "__netif_napi_del" },
	{ 0xf6ebc03b, "net_ratelimit" },
	{ 0x595b8b9b, "pci_set_power_state" },
	{ 0x82ee90dc, "timer_delete_sync" },
	{ 0xc3055d20, "usleep_range_state" },
	{ 0x682a80db, "eth_validate_addr" },
	{ 0x8a53e86c, "pci_disable_pcie_error_reporting" },
	{ 0x37a0cba, "kfree" },
	{ 0x4829a47e, "memcpy" },
	{ 0xe6ca32b4, "___pskb_trim" },
	{ 0xd109ae76, "param_array_ops" },
	{ 0x8809dbc1, "ptp_clock_index" },
	{ 0xd6651aa5, "pci_disable_msi" },
	{ 0x3721628d, "skb_add_rx_frag" },
	{ 0xaf56600a, "arm64_use_ng_mappings" },
	{ 0xb3f33bb6, "pci_num_vf" },
	{ 0xedc03953, "iounmap" },
	{ 0x8bafd9cb, "pci_prepare_to_sleep" },
	{ 0xe65c6eb7, "dma_sync_single_for_device" },
	{ 0x755b420c, "__pci_register_driver" },
	{ 0x15af7f4, "system_state" },
	{ 0x2a78242c, "dma_unmap_page_attrs" },
	{ 0x31e8d302, "pci_get_device" },
	{ 0xb09b7637, "unregister_netdev" },
	{ 0xe57eb85, "ndo_dflt_bridge_getlink" },
	{ 0x8810754a, "_find_first_bit" },
	{ 0xc5b6f236, "queue_work_on" },
	{ 0xc6725bc8, "pci_vfs_assigned" },
	{ 0x656e4a6e, "snprintf" },
	{ 0xe113bbbc, "csum_partial" },
	{ 0x5ae5183, "consume_skb" },
	{ 0x228f75de, "pci_enable_device_mem" },
	{ 0xc60d0620, "__num_online_cpus" },
	{ 0x57402efb, "skb_tstamp_tx" },
	{ 0x2df2c1f0, "skb_put" },
	{ 0xc291d122, "pci_wake_from_d3" },
	{ 0x72009703, "pci_release_selected_regions" },
	{ 0x5209a0a, "pci_request_selected_regions" },
	{ 0x14b89635, "arm64_const_caps_ready" },
	{ 0xad61c7bf, "skb_copy_bits" },
	{ 0xcfd8984d, "pci_find_ext_capability" },
	{ 0x6e720ff2, "rtnl_unlock" },
	{ 0x9e7d6bd0, "__udelay" },
	{ 0x115d7734, "__put_page" },
	{ 0xdafd6b1f, "__skb_pad" },
	{ 0x21e83e89, "device_set_wakeup_enable" },
	{ 0xc31db0ce, "is_vmalloc_addr" },
	{ 0xc1514a3b, "free_irq" },
	{ 0x90d97d, "pci_save_state" },
	{ 0xef740323, "alloc_etherdev_mqs" },
};

MODULE_INFO(depends, "");

MODULE_ALIAS("pci:v00008086d00001F40sv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d00001F41sv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d00001F45sv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d00001533sv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d00001536sv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d00001537sv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d00001538sv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d0000157Bsv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d0000157Csv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d00001539sv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d00001521sv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d00001522sv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d00001523sv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d00001524sv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d0000150Esv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d0000150Fsv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d00001527sv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d00001510sv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d00001511sv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d00001516sv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d00000438sv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d0000043Asv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d0000043Csv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d00000440sv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d000010C9sv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d0000150Asv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d00001518sv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d000010E6sv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d000010E7sv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d0000150Dsv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d00001526sv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d000010E8sv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d000010A7sv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d000010A9sv*sd*bc*sc*i*");
MODULE_ALIAS("pci:v00008086d000010D6sv*sd*bc*sc*i*");

MODULE_INFO(srcversion, "38018E00473418F0560A133");
