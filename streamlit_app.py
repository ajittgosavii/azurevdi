# VMware VDI Horizon to AWS Migration Assessment Tool
# Requirements: streamlit>=1.28.0, pandas>=1.5.0, plotly>=5.0.0, anthropic>=0.8.0

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import math
import json
import logging
from datetime import datetime, timedelta
import io
from typing import Dict, List, Tuple, Optional, Any
import numpy as np

# Configure page
st.set_page_config(
    page_title="VDI Migration Assessment Tool - VMware Horizon to AWS",
    layout="wide",
    page_icon="🖥️",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for VDI Migration Tool
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    }
    
    /* Hide Streamlit Default Elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* VDI Header */
    .vdi-header {
        background: linear-gradient(135deg, #1e40af 0%, #3730a3 50%, #7c3aed 100%);
        color: white;
        padding: 2rem 3rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
    }
    
    .vdi-header h1 {
        font-size: 2.5rem;
        font-weight: 800;
        margin-bottom: 0.5rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }
    
    .vdi-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 0.5rem;
    }
    
    /* VDI Cards */
    .vdi-card {
        background: white;
        border-radius: 16px;
        padding: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #f1f5f9;
        margin-bottom: 1.5rem;
        border-left: 4px solid #3b82f6;
    }
    
    .vdi-metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border: 2px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        text-align: center;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    .vdi-metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
        border-color: #3b82f6;
    }
    
    .metric-value-large {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1e293b;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 0.875rem;
        font-weight: 600;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* User Type Cards */
    .user-type-card {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        border: 2px solid #0ea5e9;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .user-type-card h4 {
        color: #0c4a6e;
        margin: 0;
        font-size: 1.1rem;
    }
    
    /* AWS Service Cards */
    .aws-service-card {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        border: 2px solid #f59e0b;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .aws-service-card h4 {
        color: #92400e;
        margin: 0;
        font-size: 1.1rem;
    }
    
    /* Human Resources Cards */
    .hr-card {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border: 2px solid #22c55e;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .hr-card h4 {
        color: #166534;
        margin: 0;
        font-size: 1.1rem;
    }
    
    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #f8fafc;
        padding: 0.5rem;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 60px;
        background: white;
        border-radius: 12px;
        color: #64748b;
        font-weight: 600;
        padding: 0 24px;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #3b82f6, #8b5cf6) !important;
        color: white !important;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(59, 130, 246, 0.4);
    }
    
    /* Progress bars */
    .progress-container {
        background: #f1f5f9;
        border-radius: 10px;
        padding: 4px;
        margin: 0.5rem 0;
    }
    
    .progress-bar {
        background: linear-gradient(90deg, #3b82f6, #8b5cf6);
        height: 20px;
        border-radius: 6px;
        transition: width 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

class VDIAssessmentCalculator:
    """VDI migration assessment calculator for VMware Horizon to AWS migration."""
    
    def __init__(self):
        self.user_types = {
            'task_worker': {
                'name': 'Task Worker',
                'description': 'Basic office tasks, email, web browsing',
                'cpu_cores': 2,
                'memory_gb': 4,
                'storage_gb': 50,
                'concurrent_ratio': 0.8,
                'peak_hours': 8,
                'aws_workspaces_bundle': 'Value',
                'monthly_cost_workspaces': 25
            },
            'knowledge_worker': {
                'name': 'Knowledge Worker',
                'description': 'Office productivity, light development',
                'cpu_cores': 4,
                'memory_gb': 8,
                'storage_gb': 100,
                'concurrent_ratio': 0.9,
                'peak_hours': 10,
                'aws_workspaces_bundle': 'Standard',
                'monthly_cost_workspaces': 35
            },
            'power_user': {
                'name': 'Power User',
                'description': 'Heavy applications, CAD, development',
                'cpu_cores': 8,
                'memory_gb': 16,
                'storage_gb': 250,
                'concurrent_ratio': 0.95,
                'peak_hours': 12,
                'aws_workspaces_bundle': 'Performance',
                'monthly_cost_workspaces': 68
            },
            'graphics_user': {
                'name': 'Graphics User',
                'description': '3D modeling, video editing, GPU workloads',
                'cpu_cores': 16,
                'memory_gb': 32,
                'storage_gb': 500,
                'concurrent_ratio': 0.7,
                'peak_hours': 10,
                'aws_workspaces_bundle': 'Graphics.g4dn',
                'monthly_cost_workspaces': 216
            }
        }
        
        self.aws_services = {
            'workspaces': {
                'name': 'Amazon WorkSpaces',
                'description': 'Fully managed desktop service',
                'best_for': 'Standard VDI requirements',
                'migration_complexity': 'Low',
                'management_overhead': 'Low'
            },
            'appstream': {
                'name': 'Amazon AppStream 2.0',
                'description': 'Application streaming service',
                'best_for': 'Application-specific access',
                'migration_complexity': 'Medium',
                'management_overhead': 'Medium'
            },
            'ec2_vdi': {
                'name': 'EC2-based VDI',
                'description': 'Custom VDI on EC2 instances',
                'best_for': 'Custom requirements, legacy apps',
                'migration_complexity': 'High',
                'management_overhead': 'High'
            }
        }
        
        self.migration_phases = [
            {
                'phase': 'Assessment & Planning',
                'duration_weeks': 4,
                'activities': [
                    'Current state analysis',
                    'User profiling and requirements gathering',
                    'Application compatibility assessment',
                    'Network and security requirements',
                    'Migration strategy definition'
                ],
                'deliverables': [
                    'Migration assessment report',
                    'Technical architecture design',
                    'Migration plan and timeline',
                    'Risk assessment and mitigation plan'
                ]
            },
            {
                'phase': 'Pilot Implementation',
                'duration_weeks': 6,
                'activities': [
                    'AWS environment setup',
                    'Pilot user group selection',
                    'Application migration and testing',
                    'User training development',
                    'Performance optimization'
                ],
                'deliverables': [
                    'Pilot environment',
                    'Migrated applications',
                    'Training materials',
                    'Performance baseline'
                ]
            },
            {
                'phase': 'Production Migration',
                'duration_weeks': 12,
                'activities': [
                    'Phased user migration',
                    'Application deployment',
                    'User training delivery',
                    'Support and monitoring setup',
                    'Optimization and tuning'
                ],
                'deliverables': [
                    'Production VDI environment',
                    'Migrated user base',
                    'Support procedures',
                    'Documentation'
                ]
            },
            {
                'phase': 'Optimization & Closure',
                'duration_weeks': 4,
                'activities': [
                    'Performance monitoring',
                    'Cost optimization',
                    'User feedback integration',
                    'Final documentation',
                    'Project closure'
                ],
                'deliverables': [
                    'Optimized environment',
                    'Final documentation',
                    'Lessons learned',
                    'Support handover'
                ]
            }
        ]

    def calculate_user_requirements(self, user_data: Dict) -> Dict[str, Any]:
        """Calculate technical requirements based on user distribution."""
        
        total_users = sum(user_data.values())
        if total_users == 0:
            return {'error': 'No users specified'}
        
        # Calculate concurrent users
        total_concurrent = 0
        total_cpu = 0
        total_memory = 0
        total_storage = 0
        workspaces_cost = 0
        
        user_breakdown = []
        
        for user_type, count in user_data.items():
            if count > 0:
                user_spec = self.user_types[user_type]
                concurrent = math.ceil(count * user_spec['concurrent_ratio'])
                
                cpu_required = concurrent * user_spec['cpu_cores']
                memory_required = concurrent * user_spec['memory_gb']
                storage_required = count * user_spec['storage_gb']  # Total storage, not concurrent
                cost = count * user_spec['monthly_cost_workspaces']
                
                total_concurrent += concurrent
                total_cpu += cpu_required
                total_memory += memory_required
                total_storage += storage_required
                workspaces_cost += cost
                
                user_breakdown.append({
                    'user_type': user_spec['name'],
                    'total_users': count,
                    'concurrent_users': concurrent,
                    'cpu_cores': cpu_required,
                    'memory_gb': memory_required,
                    'storage_gb': storage_required,
                    'monthly_cost': cost,
                    'workspaces_bundle': user_spec['aws_workspaces_bundle']
                })
        
        return {
            'total_users': total_users,
            'total_concurrent': total_concurrent,
            'total_cpu': total_cpu,
            'total_memory': total_memory,
            'total_storage': total_storage,
            'workspaces_monthly_cost': workspaces_cost,
            'workspaces_annual_cost': workspaces_cost * 12,
            'user_breakdown': user_breakdown,
            'average_concurrent_ratio': total_concurrent / total_users if total_users > 0 else 0
        }

    def estimate_ec2_requirements(self, user_requirements: Dict) -> Dict[str, Any]:
        """Estimate EC2 requirements for custom VDI solution."""
        
        total_concurrent = user_requirements['total_concurrent']
        total_cpu = user_requirements['total_cpu']
        total_memory = user_requirements['total_memory']
        
        # Estimate EC2 instances needed
        # Assuming m5.xlarge (4 vCPU, 16 GB) for standard desktops
        # and m5.4xlarge (16 vCPU, 64 GB) for graphics workloads
        
        # Standard instances for task/knowledge workers
        standard_concurrent = 0
        graphics_concurrent = 0
        
        for user_breakdown in user_requirements['user_breakdown']:
            if user_breakdown['workspaces_bundle'] in ['Graphics.g4dn']:
                graphics_concurrent += user_breakdown['concurrent_users']
            else:
                standard_concurrent += user_breakdown['concurrent_users']
        
        # Calculate instances needed
        users_per_standard_instance = 4  # m5.xlarge can handle ~4 concurrent standard users
        users_per_graphics_instance = 2  # g4dn.xlarge can handle ~2 concurrent graphics users
        
        standard_instances = math.ceil(standard_concurrent / users_per_standard_instance) if standard_concurrent > 0 else 0
        graphics_instances = math.ceil(graphics_concurrent / users_per_graphics_instance) if graphics_concurrent > 0 else 0
        
        # Instance pricing (on-demand, monthly)
        m5_xlarge_monthly = 0.192 * 24 * 30  # $0.192/hour * 24 hours * 30 days
        g4dn_xlarge_monthly = 0.526 * 24 * 30  # $0.526/hour * 24 hours * 30 days
        
        monthly_compute_cost = (standard_instances * m5_xlarge_monthly) + (graphics_instances * g4dn_xlarge_monthly)
        
        return {
            'standard_instances': standard_instances,
            'graphics_instances': graphics_instances,
            'total_instances': standard_instances + graphics_instances,
            'monthly_compute_cost': monthly_compute_cost,
            'annual_compute_cost': monthly_compute_cost * 12,
            'instance_details': {
                'standard': {
                    'instance_type': 'm5.xlarge',
                    'count': standard_instances,
                    'vcpu_per_instance': 4,
                    'memory_per_instance': 16,
                    'users_per_instance': users_per_standard_instance,
                    'monthly_cost_per_instance': m5_xlarge_monthly
                },
                'graphics': {
                    'instance_type': 'g4dn.xlarge',
                    'count': graphics_instances,
                    'vcpu_per_instance': 4,
                    'memory_per_instance': 16,
                    'users_per_instance': users_per_graphics_instance,
                    'monthly_cost_per_instance': g4dn_xlarge_monthly
                }
            }
        }

    def calculate_storage_requirements(self, user_requirements: Dict) -> Dict[str, Any]:
        """Calculate storage requirements and costs."""
        
        total_storage = user_requirements['total_storage']
        total_users = user_requirements['total_users']
        
        # Storage types and pricing (per GB per month)
        ebs_gp3_price = 0.08  # General Purpose SSD
        ebs_io2_price = 0.125  # Provisioned IOPS SSD
        fsx_price = 0.13  # FSx for Windows File Server
        
        # Estimates
        os_storage = total_users * 50  # 50 GB per OS image
        user_profiles = total_users * 10  # 10 GB per user profile
        shared_storage = total_users * 20  # 20 GB shared apps/data per user
        backup_storage = total_storage * 0.3  # 30% for backups
        
        total_required_storage = os_storage + user_profiles + shared_storage + backup_storage
        
        # Cost calculation
        primary_storage_cost = total_storage * ebs_gp3_price
        shared_storage_cost = shared_storage * fsx_price
        backup_storage_cost = backup_storage * ebs_gp3_price * 0.5  # Cheaper backup storage
        
        total_monthly_storage_cost = primary_storage_cost + shared_storage_cost + backup_storage_cost
        
        return {
            'total_required_storage': total_required_storage,
            'breakdown': {
                'os_images': os_storage,
                'user_profiles': user_profiles,
                'shared_storage': shared_storage,
                'backup_storage': backup_storage
            },
            'monthly_costs': {
                'primary_storage': primary_storage_cost,
                'shared_storage': shared_storage_cost,
                'backup_storage': backup_storage_cost,
                'total': total_monthly_storage_cost
            },
            'annual_cost': total_monthly_storage_cost * 12,
            'storage_recommendations': {
                'primary': 'EBS gp3 - General Purpose SSD',
                'shared': 'FSx for Windows File Server',
                'backup': 'EBS snapshots + S3 Intelligent-Tiering'
            }
        }

    def calculate_network_requirements(self, user_requirements: Dict) -> Dict[str, Any]:
        """Calculate network requirements and costs."""
        
        total_concurrent = user_requirements['total_concurrent']
        
        # Network requirements per user (Mbps)
        bandwidth_per_user = {
            'task_worker': 1.5,
            'knowledge_worker': 2.5,
            'power_user': 5.0,
            'graphics_user': 15.0
        }
        
        total_bandwidth = 0
        for user_breakdown in user_requirements['user_breakdown']:
            user_type_key = next(k for k, v in self.user_types.items() if v['name'] == user_breakdown['user_type'])
            bandwidth = user_breakdown['concurrent_users'] * bandwidth_per_user[user_type_key]
            total_bandwidth += bandwidth
        
        # Add 30% overhead for protocol and burst traffic
        total_bandwidth_with_overhead = total_bandwidth * 1.3
        
        # Network costs (monthly)
        # VPN Gateway: $36.50/month
        # Direct Connect (if needed): $162/month for 1Gbps
        # Data transfer: $0.09/GB for first 10TB
        
        estimated_data_transfer_gb = total_concurrent * 30 * 20  # 20 GB per user per month
        data_transfer_cost = min(estimated_data_transfer_gb * 0.09, 10000 * 0.09)  # First 10TB rate
        
        vpn_cost = 36.50
        nat_gateway_cost = 32.40  # $0.045/hour
        
        network_costs = {
            'vpn_gateway': vpn_cost,
            'nat_gateway': nat_gateway_cost,
            'data_transfer': data_transfer_cost,
            'total_monthly': vpn_cost + nat_gateway_cost + data_transfer_cost
        }
        
        return {
            'total_bandwidth_mbps': total_bandwidth_with_overhead,
            'estimated_data_transfer_gb': estimated_data_transfer_gb,
            'network_costs': network_costs,
            'annual_network_cost': network_costs['total_monthly'] * 12,
            'recommendations': {
                'internet_gateway': 'Required for internet access',
                'vpn_gateway': 'Site-to-Site VPN for hybrid connectivity',
                'direct_connect': 'Consider for >500 users or high bandwidth requirements',
                'nat_gateway': 'For outbound internet access from private subnets'
            }
        }

    def estimate_human_resources(self, user_requirements: Dict, migration_complexity: str) -> Dict[str, Any]:
        """Estimate human resources required for migration."""
        
        total_users = user_requirements['total_users']
        
        # Base team requirements
        base_team = {
            'project_manager': {
                'role': 'Project Manager',
                'count': 1,
                'hourly_rate': 125,
                'effort_percentage': 50,  # 50% time allocation
                'description': 'Overall project coordination and management'
            },
            'solution_architect': {
                'role': 'Solution Architect',
                'count': 1,
                'hourly_rate': 150,
                'effort_percentage': 75,
                'description': 'AWS solution design and architecture'
            },
            'vdi_specialist': {
                'role': 'VDI Migration Specialist',
                'count': 1 if total_users < 500 else 2,
                'hourly_rate': 140,
                'effort_percentage': 100,
                'description': 'VDI platform migration and optimization'
            },
            'network_engineer': {
                'role': 'Network Engineer',
                'count': 1,
                'hourly_rate': 120,
                'effort_percentage': 60,
                'description': 'Network design and connectivity setup'
            },
            'security_engineer': {
                'role': 'Security Engineer',
                'count': 1,
                'hourly_rate': 135,
                'effort_percentage': 40,
                'description': 'Security design and compliance'
            },
            'systems_engineer': {
                'role': 'Systems Engineer',
                'count': math.ceil(total_users / 250),  # 1 per 250 users
                'hourly_rate': 110,
                'effort_percentage': 80,
                'description': 'System implementation and configuration'
            },
            'application_specialist': {
                'role': 'Application Migration Specialist',
                'count': 1 if total_users < 300 else 2,
                'hourly_rate': 125,
                'effort_percentage': 70,
                'description': 'Application compatibility and migration'
            },
            'training_specialist': {
                'role': 'Training Specialist',
                'count': math.ceil(total_users / 500),  # 1 per 500 users
                'hourly_rate': 95,
                'effort_percentage': 60,
                'description': 'User training and change management'
            }
        }
        
        # Complexity multipliers
        complexity_multipliers = {
            'Low': 1.0,
            'Medium': 1.3,
            'High': 1.6
        }
        
        multiplier = complexity_multipliers.get(migration_complexity, 1.3)
        total_project_weeks = sum(phase['duration_weeks'] for phase in self.migration_phases)
        
        team_costs = []
        total_cost = 0
        
        for role_key, role_info in base_team.items():
            count = role_info['count']
            hourly_rate = role_info['hourly_rate']
            effort_percentage = role_info['effort_percentage'] / 100
            
            # Apply complexity multiplier to effort
            adjusted_effort = effort_percentage * multiplier
            adjusted_effort = min(adjusted_effort, 1.0)  # Cap at 100%
            
            hours_per_week = 40 * adjusted_effort
            total_hours = hours_per_week * total_project_weeks * count
            role_cost = total_hours * hourly_rate
            
            team_costs.append({
                'role': role_info['role'],
                'count': count,
                'hourly_rate': hourly_rate,
                'effort_percentage': adjusted_effort * 100,
                'total_hours': total_hours,
                'total_cost': role_cost,
                'description': role_info['description']
            })
            
            total_cost += role_cost
        
        # Additional costs
        additional_costs = {
            'training_materials': total_users * 50,  # $50 per user for training materials
            'project_tools': 25000,  # Project management and collaboration tools
            'contingency': total_cost * 0.15  # 15% contingency
        }
        
        total_additional = sum(additional_costs.values())
        grand_total = total_cost + total_additional
        
        return {
            'team_composition': team_costs,
            'total_team_cost': total_cost,
            'additional_costs': additional_costs,
            'total_additional_cost': total_additional,
            'grand_total_cost': grand_total,
            'project_duration_weeks': total_project_weeks,
            'complexity_multiplier': multiplier,
            'cost_breakdown': {
                'labor': total_cost,
                'materials_and_tools': additional_costs['training_materials'] + additional_costs['project_tools'],
                'contingency': additional_costs['contingency']
            }
        }

def initialize_session_state():
    """Initialize session state for VDI assessment."""
    if 'vdi_assessment' not in st.session_state:
        st.session_state.vdi_assessment = VDIAssessmentCalculator()
    
    if 'vdi_results' not in st.session_state:
        st.session_state.vdi_results = None
    
    if 'user_inputs' not in st.session_state:
        st.session_state.user_inputs = {
            'task_worker': 100,
            'knowledge_worker': 150,
            'power_user': 50,
            'graphics_user': 10,
            'migration_complexity': 'Medium',
            'current_environment': 'Azure VMware Horizon',
            'target_aws_service': 'workspaces',
            'project_timeline': 'Standard'
        }

def render_vdi_header():
    """Render the VDI tool header."""
    st.markdown("""
    <div class="vdi-header">
        <h1>🖥️ VDI Migration Assessment Tool</h1>
        <p>VMware Horizon on Azure → AWS Migration Analysis</p>
        <p style="font-size: 1rem;">📊 User Profiling • 💰 Cost Analysis • 👥 Human Resources Planning • 🔧 Technical Recommendations</p>
    </div>
    """, unsafe_allow_html=True)

def render_user_input_tab():
    """Render user input and configuration tab."""
    st.markdown("### 👥 User Distribution & Requirements")
    
    calculator = st.session_state.vdi_assessment
    
    st.markdown("""
    Configure your current user base and their requirements. This will help estimate the optimal AWS VDI solution 
    and migration approach for your organization.
    """)
    
    # Current environment info
    with st.expander("📋 Current Environment Information", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.session_state.user_inputs['current_environment'] = st.selectbox(
                "Current VDI Platform",
                ["Azure VMware Horizon", "On-premises VMware Horizon", "Citrix on Azure", "Other"],
                index=0,
                help="Select your current VDI platform"
            )
            
            st.session_state.user_inputs['migration_complexity'] = st.selectbox(
                "Expected Migration Complexity",
                ["Low", "Medium", "High"],
                index=1,
                help="Low: Standard apps, simple setup | Medium: Some legacy apps | High: Complex integrations, legacy apps"
            )
        
        with col2:
            st.session_state.user_inputs['target_aws_service'] = st.selectbox(
                "Preferred AWS VDI Service",
                ["workspaces", "appstream", "ec2_vdi"],
                format_func=lambda x: {
                    "workspaces": "Amazon WorkSpaces (Recommended)",
                    "appstream": "Amazon AppStream 2.0",
                    "ec2_vdi": "Custom EC2-based VDI"
                }[x],
                help="Select your preferred AWS VDI solution"
            )
            
            st.session_state.user_inputs['project_timeline'] = st.selectbox(
                "Project Timeline Preference",
                ["Aggressive", "Standard", "Conservative"],
                index=1,
                help="Timeline preference affects resource planning and risk"
            )
    
    # User type configuration
    st.markdown("### 👤 User Type Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Task Workers")
        st.markdown("""
        <div class="user-type-card">
            <h4>📄 Task Worker Profile</h4>
            <p><strong>Use Case:</strong> Basic office tasks, email, web browsing</p>
            <p><strong>Requirements:</strong> 2 vCPU, 4 GB RAM, 50 GB storage</p>
            <p><strong>AWS WorkSpaces:</strong> Value Bundle ($25/month)</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.session_state.user_inputs['task_worker'] = st.number_input(
            "Number of Task Workers",
            min_value=0,
            max_value=10000,
            value=st.session_state.user_inputs['task_worker'],
            step=10,
            help="Users with basic computing needs"
        )
        
        st.markdown("#### Knowledge Workers")
        st.markdown("""
        <div class="user-type-card">
            <h4>💼 Knowledge Worker Profile</h4>
            <p><strong>Use Case:</strong> Office productivity, light development</p>
            <p><strong>Requirements:</strong> 4 vCPU, 8 GB RAM, 100 GB storage</p>
            <p><strong>AWS WorkSpaces:</strong> Standard Bundle ($35/month)</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.session_state.user_inputs['knowledge_worker'] = st.number_input(
            "Number of Knowledge Workers",
            min_value=0,
            max_value=10000,
            value=st.session_state.user_inputs['knowledge_worker'],
            step=10,
            help="Users with standard productivity needs"
        )
    
    with col2:
        st.markdown("#### Power Users")
        st.markdown("""
        <div class="user-type-card">
            <h4>⚡ Power User Profile</h4>
            <p><strong>Use Case:</strong> Heavy applications, CAD, development</p>
            <p><strong>Requirements:</strong> 8 vCPU, 16 GB RAM, 250 GB storage</p>
            <p><strong>AWS WorkSpaces:</strong> Performance Bundle ($68/month)</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.session_state.user_inputs['power_user'] = st.number_input(
            "Number of Power Users",
            min_value=0,
            max_value=5000,
            value=st.session_state.user_inputs['power_user'],
            step=5,
            help="Users with high-performance computing needs"
        )
        
        st.markdown("#### Graphics Users")
        st.markdown("""
        <div class="user-type-card">
            <h4>🎨 Graphics User Profile</h4>
            <p><strong>Use Case:</strong> 3D modeling, video editing, GPU workloads</p>
            <p><strong>Requirements:</strong> 16 vCPU, 32 GB RAM, 500 GB storage</p>
            <p><strong>AWS WorkSpaces:</strong> Graphics Bundle ($216/month)</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.session_state.user_inputs['graphics_user'] = st.number_input(
            "Number of Graphics Users",
            min_value=0,
            max_value=1000,
            value=st.session_state.user_inputs['graphics_user'],
            step=1,
            help="Users requiring GPU-accelerated workloads"
        )
    
    # Calculate and run analysis
    st.markdown("---")
    
    total_users = (st.session_state.user_inputs['task_worker'] + 
                  st.session_state.user_inputs['knowledge_worker'] + 
                  st.session_state.user_inputs['power_user'] + 
                  st.session_state.user_inputs['graphics_user'])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="vdi-metric-card">
            <div class="metric-label">Total Users</div>
            <div class="metric-value-large">{total_users:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("🚀 Run VDI Assessment", type="primary", use_container_width=True):
            if total_users > 0:
                run_vdi_assessment()
            else:
                st.error("Please specify at least one user to run the assessment.")
    
    with col3:
        if st.button("🔄 Reset Configuration", use_container_width=True):
            st.session_state.user_inputs = {
                'task_worker': 100,
                'knowledge_worker': 150,
                'power_user': 50,
                'graphics_user': 10,
                'migration_complexity': 'Medium',
                'current_environment': 'Azure VMware Horizon',
                'target_aws_service': 'workspaces',
                'project_timeline': 'Standard'
            }
            st.session_state.vdi_results = None
            st.rerun()

def run_vdi_assessment():
    """Run the VDI migration assessment."""
    
    with st.spinner("🔄 Running comprehensive VDI migration assessment..."):
        try:
            calculator = st.session_state.vdi_assessment
            
            # Extract user data
            user_data = {
                'task_worker': st.session_state.user_inputs['task_worker'],
                'knowledge_worker': st.session_state.user_inputs['knowledge_worker'],
                'power_user': st.session_state.user_inputs['power_user'],
                'graphics_user': st.session_state.user_inputs['graphics_user']
            }
            
            # Calculate requirements
            user_requirements = calculator.calculate_user_requirements(user_data)
            
            if 'error' in user_requirements:
                st.error(f"Error in assessment: {user_requirements['error']}")
                return
            
            # Calculate different aspects
            ec2_requirements = calculator.estimate_ec2_requirements(user_requirements)
            storage_requirements = calculator.calculate_storage_requirements(user_requirements)
            network_requirements = calculator.calculate_network_requirements(user_requirements)
            hr_requirements = calculator.estimate_human_resources(
                user_requirements, 
                st.session_state.user_inputs['migration_complexity']
            )
            
            # Store results
            st.session_state.vdi_results = {
                'user_requirements': user_requirements,
                'ec2_requirements': ec2_requirements,
                'storage_requirements': storage_requirements,
                'network_requirements': network_requirements,
                'hr_requirements': hr_requirements,
                'inputs': st.session_state.user_inputs.copy(),
                'timestamp': datetime.now()
            }
            
            st.success("✅ VDI Migration Assessment completed successfully!")
            
        except Exception as e:
            st.error(f"❌ Error during assessment: {str(e)}")

def render_assessment_results():
    """Render the assessment results."""
    
    if st.session_state.vdi_results is None:
        st.markdown("""
        <div style="text-align: center; padding: 3rem; background: #f8fafc; border-radius: 12px; border: 2px dashed #cbd5e1;">
            <h3 style="color: #64748b; margin-bottom: 1rem;">📊 No Assessment Results</h3>
            <p style="color: #64748b; margin-bottom: 1.5rem;">Configure your VDI environment in the "User Configuration" tab and run the assessment to see detailed results here.</p>
        </div>
        """, unsafe_allow_html=True)
        return
    
    results = st.session_state.vdi_results
    user_req = results['user_requirements']
    
    # Executive Summary
    st.markdown("### 📊 Executive Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="vdi-metric-card">
            <div class="metric-label">Total Users</div>
            <div class="metric-value-large">{user_req['total_users']:,}</div>
            <div style="font-size: 0.8rem; color: #64748b;">Peak Concurrent: {user_req['total_concurrent']:,}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="vdi-metric-card">
            <div class="metric-label">AWS WorkSpaces Cost</div>
            <div class="metric-value-large">${user_req['workspaces_monthly_cost']:,.0f}</div>
            <div style="font-size: 0.8rem; color: #64748b;">per month</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        hr_cost = results['hr_requirements']['grand_total_cost']
        st.markdown(f"""
        <div class="vdi-metric-card">
            <div class="metric-label">Migration Cost</div>
            <div class="metric-value-large">${hr_cost:,.0f}</div>
            <div style="font-size: 0.8rem; color: #64748b;">total project</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        timeline = results['hr_requirements']['project_duration_weeks']
        st.markdown(f"""
        <div class="vdi-metric-card">
            <div class="metric-label">Timeline</div>
            <div class="metric-value-large">{timeline}</div>
            <div style="font-size: 0.8rem; color: #64748b;">weeks</div>
        </div>
        """, unsafe_allow_html=True)
    
    # User Distribution Chart
    st.markdown("### 👥 User Distribution Analysis")
    
    user_breakdown = user_req['user_breakdown']
    
    # Create user distribution chart
    fig_users = go.Figure()
    
    user_types = [ub['user_type'] for ub in user_breakdown]
    user_counts = [ub['total_users'] for ub in user_breakdown]
    concurrent_counts = [ub['concurrent_users'] for ub in user_breakdown]
    
    fig_users.add_trace(go.Bar(
        name='Total Users',
        x=user_types,
        y=user_counts,
        marker_color='#3b82f6'
    ))
    
    fig_users.add_trace(go.Bar(
        name='Peak Concurrent',
        x=user_types,
        y=concurrent_counts,
        marker_color='#8b5cf6'
    ))
    
    fig_users.update_layout(
        title="User Distribution by Type",
        xaxis_title="User Type",
        yaxis_title="Number of Users",
        barmode='group',
        height=400
    )
    
    st.plotly_chart(fig_users, use_container_width=True)
    
    # Detailed breakdown table
    st.markdown("#### Detailed User Requirements")
    
    user_df = pd.DataFrame(user_breakdown)
    user_df['Monthly Cost'] = user_df['monthly_cost'].apply(lambda x: f"${x:,.0f}")
    user_df['WorkSpaces Bundle'] = user_df['workspaces_bundle']
    
    display_df = user_df[['user_type', 'total_users', 'concurrent_users', 'cpu_cores', 'memory_gb', 'storage_gb', 'Monthly Cost', 'WorkSpaces Bundle']]
    display_df.columns = ['User Type', 'Total Users', 'Peak Concurrent', 'CPU Cores', 'Memory (GB)', 'Storage (GB)', 'Monthly Cost', 'WorkSpaces Bundle']
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)

def render_aws_services_comparison():
    """Render AWS services comparison and recommendations."""
    
    if st.session_state.vdi_results is None:
        st.info("💡 Run VDI assessment to see AWS service recommendations.")
        return
    
    results = st.session_state.vdi_results
    calculator = st.session_state.vdi_assessment
    
    st.markdown("### ☁️ AWS VDI Services Comparison")
    
    # Service comparison cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="aws-service-card">
            <h4>🖥️ Amazon WorkSpaces</h4>
            <p><strong>Best for:</strong> Standard VDI requirements</p>
            <p><strong>Complexity:</strong> Low</p>
            <p><strong>Management:</strong> Fully managed</p>
            <p><strong>Pricing:</strong> Per-user monthly</p>
        </div>
        """, unsafe_allow_html=True)
        
        # WorkSpaces cost breakdown
        workspaces_cost = results['user_requirements']['workspaces_monthly_cost']
        st.metric("Monthly Cost", f"${workspaces_cost:,.0f}")
        st.metric("Annual Cost", f"${workspaces_cost * 12:,.0f}")
    
    with col2:
        st.markdown("""
        <div class="aws-service-card">
            <h4>📱 Amazon AppStream 2.0</h4>
            <p><strong>Best for:</strong> Application streaming</p>
            <p><strong>Complexity:</strong> Medium</p>
            <p><strong>Management:</strong> Application-focused</p>
            <p><strong>Pricing:</strong> Per-hour usage</p>
        </div>
        """, unsafe_allow_html=True)
        
        # AppStream estimated cost (roughly 15% more than WorkSpaces)
        appstream_cost = workspaces_cost * 1.15
        st.metric("Estimated Monthly", f"${appstream_cost:,.0f}")
        st.metric("Best for", "App streaming")
    
    with col3:
        st.markdown("""
        <div class="aws-service-card">
            <h4>🛠️ Custom EC2 VDI</h4>
            <p><strong>Best for:</strong> Custom requirements</p>
            <p><strong>Complexity:</strong> High</p>
            <p><strong>Management:</strong> Self-managed</p>
            <p><strong>Pricing:</strong> Compute + storage</p>
        </div>
        """, unsafe_allow_html=True)
        
        # EC2 cost breakdown
        ec2_cost = results['ec2_requirements']['monthly_compute_cost']
        storage_cost = results['storage_requirements']['monthly_costs']['total']
        total_ec2_cost = ec2_cost + storage_cost
        
        st.metric("Monthly Compute", f"${ec2_cost:,.0f}")
        st.metric("Monthly Storage", f"${storage_cost:,.0f}")
        st.metric("Total Monthly", f"${total_ec2_cost:,.0f}")
    
    # Service recommendation
    st.markdown("### 🎯 Recommended AWS Service")
    
    user_count = results['user_requirements']['total_users']
    complexity = results['inputs']['migration_complexity']
    
    if user_count < 100 and complexity == 'Low':
        recommendation = "Amazon WorkSpaces"
        reason = "Small user base with standard requirements - WorkSpaces provides the simplest managed solution."
        color = "#10b981"
    elif user_count > 1000 or complexity == 'High':
        recommendation = "Custom EC2-based VDI"
        reason = "Large scale or complex requirements - Custom solution provides maximum flexibility and potential cost savings."
        color = "#f59e0b"
    else:
        recommendation = "Amazon WorkSpaces"
        reason = "Balanced requirements - WorkSpaces offers good mix of features, management, and cost-effectiveness."
        color = "#3b82f6"
    
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, {color}20, {color}10); 
                border: 2px solid {color}; 
                border-radius: 12px; 
                padding: 1.5rem; 
                margin: 1rem 0;">
        <h4 style="color: {color}; margin: 0;">🏆 Recommended: {recommendation}</h4>
        <p style="margin: 0.5rem 0 0 0; color: #374151;">{reason}</p>
    </div>
    """, unsafe_allow_html=True)

def render_technical_requirements():
    """Render detailed technical requirements."""
    
    if st.session_state.vdi_results is None:
        st.info("💡 Run VDI assessment to see technical requirements.")
        return
    
    results = st.session_state.vdi_results
    
    # Create tabs for different technical areas
    tech_tabs = st.tabs(["Compute", "Storage", "Network", "Migration Plan"])
    
    # Compute tab
    with tech_tabs[0]:
        st.markdown("### 💻 Compute Requirements")
        
        user_req = results['user_requirements']
        ec2_req = results['ec2_requirements']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Overall Compute Needs")
            
            compute_summary = [
                ['Metric', 'Requirement'],
                ['Total Concurrent Users', f"{user_req['total_concurrent']:,}"],
                ['Total CPU Cores Needed', f"{user_req['total_cpu']:,}"],
                ['Total Memory Needed', f"{user_req['total_memory']:,} GB"],
                ['Average Concurrent Ratio', f"{user_req['average_concurrent_ratio']:.1%}"]
            ]
            
            st.table(pd.DataFrame(compute_summary[1:], columns=compute_summary[0]))
        
        with col2:
            st.markdown("#### EC2 Instance Recommendations")
            
            ec2_details = ec2_req['instance_details']
            
            if ec2_details['standard']['count'] > 0:
                st.markdown("**Standard Workloads:**")
                st.markdown(f"• Instance Type: {ec2_details['standard']['instance_type']}")
                st.markdown(f"• Count: {ec2_details['standard']['count']} instances")
                st.markdown(f"• Users per Instance: {ec2_details['standard']['users_per_instance']}")
                st.markdown(f"• Monthly Cost: ${ec2_details['standard']['monthly_cost_per_instance'] * ec2_details['standard']['count']:,.0f}")
            
            if ec2_details['graphics']['count'] > 0:
                st.markdown("**Graphics Workloads:**")
                st.markdown(f"• Instance Type: {ec2_details['graphics']['instance_type']}")
                st.markdown(f"• Count: {ec2_details['graphics']['count']} instances")
                st.markdown(f"• Users per Instance: {ec2_details['graphics']['users_per_instance']}")
                st.markdown(f"• Monthly Cost: ${ec2_details['graphics']['monthly_cost_per_instance'] * ec2_details['graphics']['count']:,.0f}")
    
    # Storage tab
    with tech_tabs[1]:
        st.markdown("### 💾 Storage Requirements")
        
        storage_req = results['storage_requirements']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Storage Breakdown")
            
            storage_chart = go.Figure(data=[go.Pie(
                labels=['OS Images', 'User Profiles', 'Shared Storage', 'Backup Storage'],
                values=[
                    storage_req['breakdown']['os_images'],
                    storage_req['breakdown']['user_profiles'],
                    storage_req['breakdown']['shared_storage'],
                    storage_req['breakdown']['backup_storage']
                ],
                hole=.3
            )])
            
            storage_chart.update_layout(
                title="Storage Distribution (GB)",
                height=400
            )
            
            st.plotly_chart(storage_chart, use_container_width=True)
        
        with col2:
            st.markdown("#### Storage Costs & Recommendations")
            
            storage_costs = storage_req['monthly_costs']
            
            cost_breakdown = [
                ['Storage Type', 'Monthly Cost', 'Recommendation'],
                ['Primary Storage', f"${storage_costs['primary_storage']:.2f}", 'EBS gp3 - General Purpose SSD'],
                ['Shared Storage', f"${storage_costs['shared_storage']:.2f}", 'FSx for Windows File Server'],
                ['Backup Storage', f"${storage_costs['backup_storage']:.2f}", 'EBS Snapshots + S3'],
                ['Total', f"${storage_costs['total']:.2f}", f"${storage_costs['total'] * 12:.2f}/year"]
            ]
            
            st.table(pd.DataFrame(cost_breakdown[1:], columns=cost_breakdown[0]))
    
    # Network tab
    with tech_tabs[2]:
        st.markdown("### 🌐 Network Requirements")
        
        network_req = results['network_requirements']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Bandwidth Requirements")
            
            st.metric("Total Bandwidth Needed", f"{network_req['total_bandwidth_mbps']:.0f} Mbps")
            st.metric("Estimated Data Transfer", f"{network_req['estimated_data_transfer_gb']:,.0f} GB/month")
            
            st.markdown("#### Network Cost Breakdown")
            network_costs = network_req['network_costs']
            
            cost_breakdown = [
                ['Service', 'Monthly Cost'],
                ['VPN Gateway', f"${network_costs['vpn_gateway']:.2f}"],
                ['NAT Gateway', f"${network_costs['nat_gateway']:.2f}"],
                ['Data Transfer', f"${network_costs['data_transfer']:.2f}"],
                ['Total', f"${network_costs['total_monthly']:.2f}"]
            ]
            
            st.table(pd.DataFrame(cost_breakdown[1:], columns=cost_breakdown[0]))
        
        with col2:
            st.markdown("#### Network Architecture Recommendations")
            
            recommendations = network_req['recommendations']
            
            for service, description in recommendations.items():
                st.markdown(f"**{service.replace('_', ' ').title()}:** {description}")
    
    # Migration Plan tab
    with tech_tabs[3]:
        st.markdown("### 📋 Migration Plan Overview")
        
        calculator = st.session_state.vdi_assessment
        
        for i, phase in enumerate(calculator.migration_phases, 1):
            with st.expander(f"Phase {i}: {phase['phase']} ({phase['duration_weeks']} weeks)", expanded=i==1):
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Key Activities:**")
                    for activity in phase['activities']:
                        st.markdown(f"• {activity}")
                
                with col2:
                    st.markdown("**Deliverables:**")
                    for deliverable in phase['deliverables']:
                        st.markdown(f"• {deliverable}")

def render_human_resources_tab():
    """Render human resources requirements and costs."""
    
    if st.session_state.vdi_results is None:
        st.info("💡 Run VDI assessment to see human resources requirements.")
        return
    
    results = st.session_state.vdi_results
    hr_req = results['hr_requirements']
    
    st.markdown("### 👥 Human Resources Requirements")
    
    # Executive summary
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="hr-card">
            <h4>Total Project Cost</h4>
            <p style="font-size: 1.5rem; font-weight: bold;">${hr_req['grand_total_cost']:,.0f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="hr-card">
            <h4>Labor Cost</h4>
            <p style="font-size: 1.5rem; font-weight: bold;">${hr_req['total_team_cost']:,.0f}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="hr-card">
            <h4>Project Duration</h4>
            <p style="font-size: 1.5rem; font-weight: bold;">{hr_req['project_duration_weeks']} weeks</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        team_size = len(hr_req['team_composition'])
        st.markdown(f"""
        <div class="hr-card">
            <h4>Team Size</h4>
            <p style="font-size: 1.5rem; font-weight: bold;">{team_size} roles</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Team composition
    st.markdown("### 👨‍💼 Team Composition & Costs")
    
    team_data = []
    for member in hr_req['team_composition']:
        team_data.append({
            'Role': member['role'],
            'Count': member['count'],
            'Hourly Rate': f"${member['hourly_rate']}",
            'Effort %': f"{member['effort_percentage']:.0f}%",
            'Total Hours': f"{member['total_hours']:,.0f}",
            'Total Cost': f"${member['total_cost']:,.0f}",
            'Description': member['description']
        })
    
    team_df = pd.DataFrame(team_data)
    st.dataframe(team_df, use_container_width=True, hide_index=True)
    
    # Cost breakdown chart
    st.markdown("### 💰 Cost Breakdown Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Cost breakdown pie chart
        cost_breakdown = hr_req['cost_breakdown']
        
        fig_costs = go.Figure(data=[go.Pie(
            labels=['Labor', 'Materials & Tools', 'Contingency'],
            values=[
                cost_breakdown['labor'],
                cost_breakdown['materials_and_tools'],
                cost_breakdown['contingency']
            ],
            hole=.3
        )])
        
        fig_costs.update_layout(
            title="Project Cost Distribution",
            height=400
        )
        
        st.plotly_chart(fig_costs, use_container_width=True)
    
    with col2:
        # Role cost distribution
        role_costs = [member['total_cost'] for member in hr_req['team_composition']]
        role_names = [member['role'] for member in hr_req['team_composition']]
        
        fig_roles = go.Figure(data=[go.Bar(
            x=role_names,
            y=role_costs,
            marker_color='#3b82f6'
        )])
        
        fig_roles.update_layout(
            title="Cost by Role",
            xaxis_title="Role",
            yaxis_title="Cost ($)",
            height=400,
            xaxis_tickangle=-45
        )
        
        st.plotly_chart(fig_roles, use_container_width=True)
    
    # Additional costs breakdown
    st.markdown("### 📊 Additional Costs")
    
    additional_costs = hr_req['additional_costs']
    
    additional_data = [
        ['Cost Category', 'Amount', 'Description'],
        ['Training Materials', f"${additional_costs['training_materials']:,.0f}", 'User training materials and resources'],
        ['Project Tools', f"${additional_costs['project_tools']:,.0f}", 'Project management and collaboration tools'],
        ['Contingency (15%)', f"${additional_costs['contingency']:,.0f}", 'Risk mitigation and unforeseen costs'],
        ['Total Additional', f"${hr_req['total_additional_cost']:,.0f}", 'Total non-labor costs']
    ]
    
    st.table(pd.DataFrame(additional_data[1:], columns=additional_data[0]))

def render_cost_summary_tab():
    """Render comprehensive cost summary and comparison."""
    
    if st.session_state.vdi_results is None:
        st.info("💡 Run VDI assessment to see cost analysis.")
        return
    
    results = st.session_state.vdi_results
    
    st.markdown("### 💰 Comprehensive Cost Analysis")
    
    # Extract costs
    workspaces_monthly = results['user_requirements']['workspaces_monthly_cost']
    workspaces_annual = workspaces_monthly * 12
    
    ec2_monthly = results['ec2_requirements']['monthly_compute_cost']
    storage_monthly = results['storage_requirements']['monthly_costs']['total']
    network_monthly = results['network_requirements']['network_costs']['total_monthly']
    
    ec2_total_monthly = ec2_monthly + storage_monthly + network_monthly
    ec2_annual = ec2_total_monthly * 12
    
    migration_cost = results['hr_requirements']['grand_total_cost']
    
    # AWS Service Cost Comparison
    st.markdown("### ☁️ AWS Service Cost Comparison")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="aws-service-card">
            <h4>🖥️ Amazon WorkSpaces</h4>
            <p><strong>Monthly:</strong> ${:,.0f}</p>
            <p><strong>Annual:</strong> ${:,.0f}</p>
            <p><strong>Management:</strong> Fully Managed</p>
        </div>
        """.format(workspaces_monthly, workspaces_annual), unsafe_allow_html=True)
    
    with col2:
        appstream_monthly = workspaces_monthly * 1.15  # Estimated 15% higher
        appstream_annual = appstream_monthly * 12
        st.markdown("""
        <div class="aws-service-card">
            <h4>📱 Amazon AppStream 2.0</h4>
            <p><strong>Monthly:</strong> ${:,.0f}</p>
            <p><strong>Annual:</strong> ${:,.0f}</p>
            <p><strong>Management:</strong> Application Focused</p>
        </div>
        """.format(appstream_monthly, appstream_annual), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="aws-service-card">
            <h4>🛠️ Custom EC2 VDI</h4>
            <p><strong>Monthly:</strong> ${:,.0f}</p>
            <p><strong>Annual:</strong> ${:,.0f}</p>
            <p><strong>Management:</strong> Self-Managed</p>
        </div>
        """.format(ec2_total_monthly, ec2_annual), unsafe_allow_html=True)
    
    # Cost comparison chart
    st.markdown("### 📊 Annual Cost Comparison")
    
    services = ['Amazon WorkSpaces', 'Amazon AppStream 2.0', 'Custom EC2 VDI']
    annual_costs = [workspaces_annual, appstream_annual, ec2_annual]
    colors = ['#10b981', '#f59e0b', '#3b82f6']
    
    fig_comparison = go.Figure(data=[go.Bar(
        x=services,
        y=annual_costs,
        marker_color=colors,
        text=[f'${cost:,.0f}' for cost in annual_costs],
        textposition='auto'
    )])
    
    fig_comparison.update_layout(
        title="Annual Operating Cost Comparison",
        xaxis_title="AWS Service",
        yaxis_title="Annual Cost ($)",
        height=500
    )
    
    st.plotly_chart(fig_comparison, use_container_width=True)
    
    # Migration cost analysis
    st.markdown("### 🚀 Migration Investment Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### One-Time Migration Costs")
        migration_breakdown = results['hr_requirements']['cost_breakdown']
        
        migration_data = [
            ['Cost Category', 'Amount'],
            ['Labor Costs', f"${migration_breakdown['labor']:,.0f}"],
            ['Materials & Tools', f"${migration_breakdown['materials_and_tools']:,.0f}"],
            ['Contingency', f"${migration_breakdown['contingency']:,.0f}"],
            ['Total Migration Cost', f"${migration_cost:,.0f}"]
        ]
        
        st.table(pd.DataFrame(migration_data[1:], columns=migration_data[0]))
    
    with col2:
        st.markdown("#### ROI Analysis (5-Year)")
        
        # Calculate 5-year TCO for different scenarios
        years = 5
        
        # Assume current Azure cost is 20% higher than AWS WorkSpaces
        current_azure_annual = workspaces_annual * 1.2
        
        # 5-year costs including migration
        workspaces_5yr = (workspaces_annual * years) + migration_cost
        azure_5yr = current_azure_annual * years
        
        savings_5yr = azure_5yr - workspaces_5yr
        roi_percentage = (savings_5yr / migration_cost) * 100 if migration_cost > 0 else 0
        
        roi_data = [
            ['Metric', 'Value'],
            ['Current Azure (5yr)', f"${azure_5yr:,.0f}"],
            ['AWS WorkSpaces (5yr)', f"${workspaces_5yr:,.0f}"],
            ['5-Year Savings', f"${savings_5yr:,.0f}"],
            ['ROI %', f"{roi_percentage:.1f}%"],
            ['Payback Period', f"{(migration_cost / (azure_5yr - workspaces_annual)) * 12:.0f} months" if azure_5yr > workspaces_annual else "N/A"]
        ]
        
        st.table(pd.DataFrame(roi_data[1:], columns=roi_data[0]))
    
    # Total Cost of Ownership chart
    st.markdown("### 📈 Total Cost of Ownership (5-Year)")
    
    years_range = list(range(1, 6))
    azure_cumulative = [current_azure_annual * year for year in years_range]
    workspaces_cumulative = [migration_cost + (workspaces_annual * year) for year in years_range]
    ec2_cumulative = [migration_cost * 1.2 + (ec2_annual * year) for year in years_range]  # Assume 20% higher migration cost for EC2
    
    fig_tco = go.Figure()
    
    fig_tco.add_trace(go.Scatter(
        x=years_range,
        y=azure_cumulative,
        mode='lines+markers',
        name='Current Azure VMware',
        line=dict(color='#ef4444', width=3)
    ))
    
    fig_tco.add_trace(go.Scatter(
        x=years_range,
        y=workspaces_cumulative,
        mode='lines+markers',
        name='AWS WorkSpaces',
        line=dict(color='#10b981', width=3)
    ))
    
    fig_tco.add_trace(go.Scatter(
        x=years_range,
        y=ec2_cumulative,
        mode='lines+markers',
        name='Custom EC2 VDI',
        line=dict(color='#3b82f6', width=3)
    ))
    
    fig_tco.update_layout(
        title="5-Year Total Cost of Ownership Comparison",
        xaxis_title="Year",
        yaxis_title="Cumulative Cost ($)",
        height=500,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_tco, use_container_width=True)

def main():
    """Main application function."""
    
    # Initialize session state
    initialize_session_state()
    
    # Render header
    render_vdi_header()
    
    # Main tabs
    main_tabs = st.tabs([
        "User Configuration", 
        "Assessment Results", 
        "AWS Services", 
        "Technical Requirements", 
        "Human Resources", 
        "Cost Analysis"
    ])
    
    # User Configuration tab
    with main_tabs[0]:
        render_user_input_tab()
    
    # Assessment Results tab
    with main_tabs[1]:
        render_assessment_results()
    
    # AWS Services tab
    with main_tabs[2]:
        render_aws_services_comparison()
    
    # Technical Requirements tab
    with main_tabs[3]:
        render_technical_requirements()
    
    # Human Resources tab
    with main_tabs[4]:
        render_human_resources_tab()
    
    # Cost Analysis tab
    with main_tabs[5]:
        render_cost_summary_tab()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #6b7280; font-size: 0.875rem; padding: 2rem 0;">
        <strong>VDI Migration Assessment Tool v1.0</strong><br>
        VMware Horizon on Azure → AWS Migration Analysis<br>
        <em>🖥️ User Profiling • 💰 Cost Analysis • 👥 HR Planning • 🔧 Technical Design</em>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()