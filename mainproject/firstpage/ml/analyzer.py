"""
Academic Analysis Logic
This module contains the rule-based logic for analyzing student academic performance
and providing recommendations, cautions, and suggestions.
Combines Claude's enhanced risk assessment with C# trend analysis logic.
"""

def analyse_student(data):
    """
    Analyzes student academic data and returns recommendations.
    
    Args:
        data (dict): Contains gpa_cgpa, cgpa_trend, department, past_courses, current_courses
        
    Returns:
        tuple: (result_dict, status_code)
    """
    try:
        cgpa = data.get('gpa_cgpa', 0)
        cgpa_trend = data.get('cgpa_trend', '')
        department = data.get('department', '')
        past_courses = data.get('past_courses', [])
        current_courses = data.get('current_courses', [])
        
        # ═══════════════════════════════════════════════════════
        # VALIDATION
        # ═══════════════════════════════════════════════════════
        if cgpa < 0 or cgpa > 5.0:
            return {
                'error': 'GPA/CGPA must be between 0.00 and 5.00',
                'risk_level': 'Unknown'
            }, 400
        
        if len(past_courses) < 6 or len(past_courses) > 9:
            return {
                'error': 'Past courses must be between 6 and 9',
                'risk_level': 'Unknown'
            }, 400
        
        if len(current_courses) < 6 or len(current_courses) > 9:
            return {
                'error': 'Current courses must be between 6 and 9',
                'risk_level': 'Unknown'
            }, 400
        
        # Initialize result dictionary
        result = {
            'risk_level': '',
            'cgpa_status': '',
            'cgpa_trend': '',
            'trend_description': '',
            'cautions': [],
            'suggestions': [],
            'explanation': ''
        }
        
        # ═══════════════════════════════════════════════════════
        # 1. RISK LEVEL ASSESSMENT (Claude's version)
        # ═══════════════════════════════════════════════════════
        if cgpa >= 4.5:
            result['risk_level'] = 'Excellent'
            result['cgpa_status'] = 'Outstanding performance'
        elif cgpa >= 3.5:
            result['risk_level'] = 'Good'
            result['cgpa_status'] = 'Above average performance'
        elif cgpa >= 2.5:
            result['risk_level'] = 'Moderate'
            result['cgpa_status'] = 'Average performance - room for improvement'
        elif cgpa >= 2.0:
            result['risk_level'] = 'At Risk'
            result['cgpa_status'] = 'Below average - needs attention'
        else:
            result['risk_level'] = 'High Risk'
            result['cgpa_status'] = 'Critical - immediate intervention needed'
        
        # ═══════════════════════════════════════════════════════
        # 2. CGPA TREND ANALYSIS (C# logic + Claude's descriptions)
        # ═══════════════════════════════════════════════════════
        trend_list = []
        if isinstance(cgpa_trend, str):
            for x in cgpa_trend.split(','):
                try:
                    trend_list.append(float(x.strip()))
                except ValueError:
                    pass
        elif isinstance(cgpa_trend, list):
            trend_list = cgpa_trend
        
        if len(trend_list) >= 2:
            last = trend_list[-1]
            prev = trend_list[-2]
            
            # Always stable for excellent performance (C# logic)
            if cgpa >= 4.50:
                result['cgpa_trend'] = 'Stable'
                result['trend_description'] = '📊 Maintaining excellent performance'
            elif last > prev:
                result['cgpa_trend'] = 'Improving'
                trend_change = last - prev
                if trend_change > 0.3:
                    result['trend_description'] = '📈 CGPA is improving significantly - keep up the good work!'
                else:
                    result['trend_description'] = '📈 CGPA is improving steadily'
            elif last < prev:
                result['cgpa_trend'] = 'Declining'
                trend_change = prev - last
                if trend_change > 0.3:
                    result['trend_description'] = '⚠️ WARNING: CGPA is declining significantly'
                else:
                    result['trend_description'] = '⚠️ CGPA is declining - needs attention'
            else:
                result['cgpa_trend'] = 'Stable'
                result['trend_description'] = '📊 CGPA trend is stable'
        else:
            result['cgpa_trend'] = 'Not enough data'
            result['trend_description'] = 'Not enough trend data available'
        
        # ═══════════════════════════════════════════════════════
        # 3. EXCELLENT PERFORMANCE (4.50 - 5.00) - Return Early
        # ═══════════════════════════════════════════════════════
        if cgpa >= 4.50:
            result['suggestions'].append(
                "Outstanding academic performance. You are doing excellently well — maintain consistency, "
                "discipline, and healthy study habits."
            )
            result['explanation'] = (
                "Student demonstrates excellent academic performance based on GPA/CGPA and sustained results."
            )
            # ✅ No cautions for excellent students
            return result, 200
        
        # ═══════════════════════════════════════════════════════
        # 4. CURRENT COURSE STATUS ANALYSIS
        # ═══════════════════════════════════════════════════════
        registered_count = sum(1 for c in current_courses if c.get('status', '').lower() == 'registered')
        in_progress_count = sum(1 for c in current_courses if c.get('status', '').lower() == 'in progress')
        carried_over_count = sum(1 for c in current_courses if c.get('status', '').lower() == 'carried over')
        
        # ═══════════════════════════════════════════════════════
        # 5. CAUTIONS - ONLY FOR "AT RISK" AND "HIGH RISK"
        # ═══════════════════════════════════════════════════════
        if result['risk_level'] in ['At Risk', 'High Risk']:
            # Add trend description as caution if declining
            if result['cgpa_trend'] == 'Declining':
                result['cautions'].append(result['trend_description'])
            
            # Carried over courses caution
            if carried_over_count > 0:
                result['cautions'].append(
                    f"You have {carried_over_count} carried over course(s). "
                    "Prioritize these to avoid accumulation."
                )
        
        # ═══════════════════════════════════════════════════════
        # 6. MODERATE RISK + DECLINING TREND (Special case)
        # ═══════════════════════════════════════════════════════
        if result['risk_level'] == 'Moderate' and result['cgpa_trend'] == 'Declining':
            result['cautions'].append(
                "Your academic performance shows signs of decline."
            )
            result['suggestions'].append(
                "Increase study time, review weak subjects, and seek academic support early."
            )
        
        # ═══════════════════════════════════════════════════════
        # 7. AT RISK HANDLING
        # ═══════════════════════════════════════════════════════
        if result['risk_level'] == 'At Risk':
            result['cautions'].append(
                "Academic performance needs attention."
            )
            result['suggestions'].extend([
                "Schedule a meeting with your academic advisor",
                "Join study groups for challenging courses",
                "Utilize office hours with professors",
                "Review time management and study strategies"
            ])
        
        # ═══════════════════════════════════════════════════════
        # 8. HIGH RISK HANDLING
        # ═══════════════════════════════════════════════════════
        if result['risk_level'] == 'High Risk':
            result['cautions'].append(
                "⚠️ CRITICAL: High academic risk detected."
            )
            result['suggestions'].extend([
                "URGENT: Meet with your academic advisor this week",
                "Consider academic probation support services",
                "Reduce course load where possible, focus on core courses",
                "Develop a detailed study schedule with achievable goals",
                "Explore tutoring resources available in your department"
            ])
        
        # ═══════════════════════════════════════════════════════
        # 9. RISK-SPECIFIC SUGGESTIONS
        # ═══════════════════════════════════════════════════════
        if result['risk_level'] == 'Good':
            result['suggestions'].extend([
                "Maintain your current study habits",
                "Consider taking on leadership roles in student organizations",
                "Explore research opportunities or advanced courses"
            ])
        
        if result['risk_level'] == 'Moderate':
            result['suggestions'].extend([
                "Focus on improving grades in core courses",
                "Participate actively in class discussions",
                "Form study groups with high-performing peers",
                "Maintain a balanced study routine and prioritize core departmental courses"
            ])
        
        # ═══════════════════════════════════════════════════════
        # 10. EXPLANATION
        # ═══════════════════════════════════════════════════════
        result['explanation'] = (
            "This analysis considers GPA/CGPA level, CGPA trend progression, "
            "course load constraints, and standard university advising principles."
        )
        
        return result, 200
        
    except Exception as e:
        return {
            'error': f'Analysis failed: {str(e)}',
            'risk_level': 'Unknown',
            'cgpa_trend': 'Unknown',
            'cgpa_status': 'Unknown',
            'trend_description': '',
            'cautions': [],
            'suggestions': [],
            'explanation': 'Unable to analyze data due to an error'
        }, 500
