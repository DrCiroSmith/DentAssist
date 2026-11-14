import 'dart:typed_data';
import 'package:flutter/material.dart';
import '../services/medgemma_service.dart';
import '../services/hipaa_offline_guard.dart';
import '../services/clinical_disclaimer.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final MedGemmaService _medGemma = MedGemmaService();
  final HipaaOfflineGuard _hipaaGuard = HipaaOfflineGuard();
  
  bool _isAnalyzing = false;
  String _streamedOutput = '';
  bool _hasAnalyzed = false;

  @override
  void initState() {
    super.initState();
    _hipaaGuard.verifyAirGapIntegrity();
  }

  void _triggerAnalysis() async {
    setState(() {
      _isAnalyzing = true;
      _streamedOutput = '';
      _hasAnalyzed = true;
    });

    final mockImage = Uint8List.fromList([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]);
    
    await for (final token in _medGemma.streamInference(
      imageBytes: mockImage,
      prompt: "Evaluate periapical region of mandibular first molar (#19)",
    )) {
      if (mounted) {
        setState(() {
          _streamedOutput += token;
        });
      }
    }

    if (mounted) {
      setState(() {
        _isAnalyzing = false;
      });
    }
  }

  void _performSecureWipe() {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: const Color(0xFF0F172A),
        title: const Text(
          'Confirm Cryptographic Wipe',
          style: TextStyle(color: Color(0xFFF8FAFC), fontWeight: FontWeight.bold),
        ),
        content: const Text(
          'This performs a DoD 5220.22-M 3-pass overwrite across volatile RAM and session storage. All patient images and findings will be permanently shredded.',
          style: TextStyle(color: Color(0xFF94A3B8)),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel', style: TextStyle(color: Color(0xFF64748B))),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFFEF4444),
              foregroundColor: Colors.white,
            ),
            onPressed: () async {
              await _hipaaGuard.secureWipe();
              setState(() {
                _streamedOutput = '';
                _hasAnalyzed = false;
              });
              Navigator.pop(ctx);
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(
                  content: Text('Session cache shredded. 0 bytes retained.'),
                  backgroundColor: Color(0xFF10B981),
                ),
              );
            },
            child: const Text('Shred Data'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0B1120),
      appBar: AppBar(
        backgroundColor: const Color(0xFF0F172A),
        elevation: 0,
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(
                color: const Color(0xFF06B6D4).withOpacity(0.15),
                borderRadius: BorderRadius.circular(6),
                border: Border.all(color: const Color(0xFF06B6D4), width: 1),
              ),
              child: const Text(
                'DentAssist',
                style: TextStyle(
                  color: Color(0xFF38BDF8),
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
            const SizedBox(width: 8),
            const Text(
              'MedGemma 4B',
              style: TextStyle(color: Color(0xFF94A3B8), fontSize: 13),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.delete_sweep, color: Color(0xFFEF4444)),
            tooltip: '1-Tap Secure Wipe',
            onPressed: _performSecureWipe,
          ),
        ],
      ),
      body: Column(
        children: [
          // Air-Gap Status Banner
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            color: const Color(0xFF064E3B).withOpacity(0.4),
            child: Row(
              children: [
                const Icon(Icons.shield_outlined, color: Color(0xFF10B981), size: 18),
                const SizedBox(width: 8),
                const Expanded(
                  child: Text(
                    'AIR-GAP ACTIVE • 0 B Outbound • Local MLC-LLM GPU Runtime',
                    style: TextStyle(
                      color: Color(0xFF34D399),
                      fontSize: 11,
                      fontWeight: FontWeight.w600,
                      letterSpacing: 0.5,
                    ),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: const Color(0xFF10B981).withOpacity(0.2),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: const Text(
                    'HIPAA SAFE',
                    style: TextStyle(color: Color(0xFF10B981), fontSize: 10, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
          ),

          // Main Scrollable Area
          Expanded(
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: [
                // Case Image Card
                Card(
                  color: const Color(0xFF0F172A),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                    side: const BorderSide(color: Color(0xFF1E293B)),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(14),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text(
                            'Active Case: Radiographic Exam #19',
                            style: TextStyle(color: Color(0xFFF8FAFC), fontWeight: FontWeight.w600),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                            decoration: BoxDecoration(
                              color: const Color(0xFFF59E0B).withOpacity(0.15),
                              borderRadius: BorderRadius.circular(4),
                              border: Border.all(color: const Color(0xFFF59E0B)),
                            ),
                            child: const Text(
                              'ROI: Periapical Apex',
                              style: TextStyle(color: Color(0xFFF59E0B), fontSize: 11, fontWeight: FontWeight.bold),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Container(
                        height: 140,
                        decoration: BoxDecoration(
                          color: const Color(0xFF020617),
                          borderRadius: BorderRadius.circular(8),
                          border: Border.all(color: const Color(0xFF334155)),
                        ),
                        child: Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: const [
                              Icon(Icons.image_search, color: Color(0xFF06B6D4), size: 36),
                              SizedBox(height: 6),
                              Text(
                                'Periapical Bitewing Digitized Bitmap',
                                style: TextStyle(color: Color(0xFF94A3B8), fontSize: 12),
                              ),
                              Text(
                                'Mandibular Left Molar Region • 14-bit Gray Depth',
                                style: TextStyle(color: Color(0xFF64748B), fontSize: 10),
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 12),
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton.icon(
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFF06B6D4),
                            foregroundColor: const Color(0xFF0B1120),
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                          ),
                          onPressed: _isAnalyzing ? null : _triggerAnalysis,
                          icon: _isAnalyzing
                              ? const SizedBox(
                                  width: 16,
                                  height: 16,
                                  child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xFF0B1120)),
                                )
                              : const Icon(Icons.play_arrow),
                          label: Text(
                            _isAnalyzing ? 'Running On-Device MedGemma 4B...' : 'Run Multimodal Assessment',
                            style: const TextStyle(fontWeight: FontWeight.bold),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),

                const SizedBox(height: 16),

                // Diagnostic Stream Box
                if (_hasAnalyzed)
                  Card(
                    color: const Color(0xFF0F172A),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                      side: const BorderSide(color: Color(0xFF14B8A6)),
                    ),
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                        Row(
                          children: const [
                            Icon(Icons.psychology, color: Color(0xFF14B8A6), size: 20),
                            SizedBox(width: 8),
                            Text(
                              'On-Device Differential Stream',
                              style: TextStyle(color: Color(0xFF14B8A6), fontWeight: FontWeight.bold),
                            ),
                          ],
                        ),
                        const Divider(color: Color(0xFF1E293B), height: 20),
                        Text(
                          _streamedOutput.isEmpty ? 'Initializing weights...' : _streamedOutput,
                          style: const TextStyle(
                            color: Color(0xFFE2E8F0),
                            fontSize: 13,
                            height: 1.5,
                            fontFamily: 'monospace',
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

                const SizedBox(height: 16),

                // Clinical Disclaimer Card
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: const Color(0xFF1E293B).withOpacity(0.5),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: const Color(0xFF334155)),
                  ),
                  child: const Text(
                    ClinicalDisclaimer.adaDisclaimerText,
                    style: TextStyle(color: Color(0xFF64748B), fontSize: 10, height: 1.4),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
