import 'package:flutter/material.dart';

class OutfitScheduleScreen extends StatelessWidget {
  const OutfitScheduleScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(
        title: Text(
          'Outfit Schedule',
          style: TextStyle(
            color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.black,
            fontSize: 18,
            fontWeight: FontWeight.w600,
          ),
        ),
        backgroundColor: Colors.transparent,
        elevation: 0,
        iconTheme: IconThemeData(
            color: Theme.of(context).iconTheme.color ?? Colors.black),
        actions: [
          IconButton(
            icon: Icon(Icons.add_rounded, color: Theme.of(context).colorScheme.primary),
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('Plan new outfit coming soon!')),
              );
            },
          )
        ],
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'This Week',
                style: TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                  color: Theme.of(context).textTheme.bodyLarge?.color ?? Colors.black,
                ),
              ),
              const SizedBox(height: 24),
              
              _DayScheduleCard(
                day: 'Today',
                date: '28 Jul',
                hasOutfit: true,
                outfitName: 'Casual Office',
              ),
              const SizedBox(height: 16),
              
              _DayScheduleCard(
                day: 'Tomorrow',
                date: '29 Jul',
                hasOutfit: true,
                outfitName: 'Dinner Date',
              ),
              const SizedBox(height: 16),

              _DayScheduleCard(
                day: 'Wednesday',
                date: '30 Jul',
                hasOutfit: false,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _DayScheduleCard extends StatelessWidget {
  final String day;
  final String date;
  final bool hasOutfit;
  final String? outfitName;

  const _DayScheduleCard({
    required this.day,
    required this.date,
    required this.hasOutfit,
    this.outfitName,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Theme.of(context).dividerColor.withValues(alpha: 0.5)),
      ),
      child: Row(
        children: [
          // Date Column
          Column(
            children: [
              Text(
                day,
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.w600,
                  color: Theme.of(context).textTheme.bodyLarge?.color,
                ),
              ),
              Text(
                date,
                style: TextStyle(
                  fontSize: 12,
                  color: Theme.of(context).textTheme.bodyMedium?.color ?? Colors.grey,
                ),
              ),
            ],
          ),
          const SizedBox(width: 24),
          
          // Separator
          Container(
            width: 1,
            height: 40,
            color: Theme.of(context).dividerColor,
          ),
          const SizedBox(width: 24),

          // Content
          Expanded(
            child: hasOutfit
                ? Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        outfitName ?? '',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Theme.of(context).textTheme.bodyLarge?.color,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Scheduled',
                        style: TextStyle(
                          fontSize: 12,
                          color: Theme.of(context).colorScheme.primary,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  )
                : Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'No outfit planned',
                        style: TextStyle(
                          fontSize: 14,
                          color: Theme.of(context).textTheme.bodyMedium?.color ?? Colors.grey,
                          fontStyle: FontStyle.italic,
                        ),
                      ),
                    ],
                  ),
          ),
          
          if (!hasOutfit)
            ElevatedButton(
              onPressed: () {},
              style: ElevatedButton.styleFrom(
                backgroundColor: Theme.of(context).colorScheme.surface,
                foregroundColor: Theme.of(context).colorScheme.primary,
                elevation: 0,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
              ),
              child: const Text('Plan'),
            )
        ],
      ),
    );
  }
}
