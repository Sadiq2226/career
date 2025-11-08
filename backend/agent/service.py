from __future__ import annotations

from typing import Dict, Any, List
import statistics
import os
from datetime import datetime, timedelta
import math

import pandas as pd

from .config import settings
from .data_loader import load_structured_data, load_unstructured_docs
from .chains import OfflineRetriever, GeminiRetriever, offline_summarize, gemini_summarize, synthesize_parent_friendly_insights, gemini_synthesize_insights, score_support_index


def clean_float_value(value: float) -> float:
    """Clean float values to be JSON serializable."""
    if pd.isna(value) or value == float('inf') or value == float('-inf'):
        return 0.0
    if math.isnan(value):
        return 0.0
    return float(value)


class AgentService:
    def __init__(self, use_real_data: bool = True) -> None:
        self.use_real_data = use_real_data
        self.data_cache_time = None
        self.cache_duration = timedelta(hours=1)  # Cache for 1 hour
        self._load_data()
    
    def _load_data(self) -> None:
        """Load data with caching mechanism."""
        should_refresh = (
            self.data_cache_time is None or 
            datetime.now() - self.data_cache_time > self.cache_duration
        )
        
        if should_refresh:
            self.employment_df, self.salary_df, self.support_df = load_structured_data(
                settings.data_dir, use_real_data=self.use_real_data
            )
            self.docs = load_unstructured_docs(settings.data_dir)
            # Use Gemini retriever if available, otherwise fallback to offline
            if settings.online_mode:
                self.retriever = GeminiRetriever(self.docs)
            else:
                self.retriever = OfflineRetriever(self.docs)
            self.data_cache_time = datetime.now()
            print(f"Data refreshed at {self.data_cache_time}")
        else:
            print(f"Using cached data from {self.data_cache_time}")

    # ---------- Core Analyses ----------
    def analyze_employment(self, degree: str | None = None, year: int | None = None) -> Dict[str, Any]:
        """Enhanced employment analysis with real-time insights."""
        self._load_data()  # Ensure fresh data
        df = self.employment_df.copy()
        
        # Apply filters
        if degree:
            df = df[df["degree"].str.lower() == degree.lower()]
        if year:
            df = df[df["year"] == int(year)]
            
        if df.empty:
            return {
                "summary": "No matching records found for the specified criteria.",
                "top_institutions": [],
                "average_employment_rate": None,
                "data_quality": "No data available"
            }
        
        # Enhanced analysis with NaN/Inf handling
        grouped = df.groupby(["institution"]).agg({
            "employment_rate": ["mean", "std", "count"],
            "median_salary": "mean"
        }).reset_index()
        
        # Flatten column names
        grouped.columns = ["institution", "avg_employment_rate", "employment_std", "record_count", "avg_salary"]
        
        # Handle NaN and Inf values
        for col in ["avg_employment_rate", "employment_std", "avg_salary"]:
            grouped[col] = grouped[col].replace([float('inf'), float('-inf')], 0)
            grouped[col] = grouped[col].fillna(0)
        
        grouped = grouped.sort_values("avg_employment_rate", ascending=False)
        
        # Convert to dict and clean values
        top_institutions = grouped.head(5).to_dict(orient="records")
        for item in top_institutions:
            for key, value in item.items():
                if isinstance(value, float):
                    if pd.isna(value) or value == float('inf') or value == float('-inf'):
                        item[key] = 0
                    else:
                        item[key] = round(value, 2)
        
        avg_rate = df["employment_rate"].mean()
        median_salary = df["median_salary"].median()
        
        # Clean final values
        avg_rate = 0 if pd.isna(avg_rate) or avg_rate == float('inf') or avg_rate == float('-inf') else round(avg_rate, 2)
        median_salary = 0 if pd.isna(median_salary) or median_salary == float('inf') or median_salary == float('-inf') else round(median_salary, 0)
        
        # Calculate trends
        if len(df) > 1:
            recent_data = df[df["year"] == df["year"].max()]
            older_data = df[df["year"] == df["year"].min()]
            trend = "improving" if recent_data["employment_rate"].mean() > older_data["employment_rate"].mean() else "declining"
        else:
            trend = "stable"
        
        return {
            "summary": f"Analysis of {len(df)} records shows average employment rate of {avg_rate}% with median salary of ₹{median_salary:,}. Trend: {trend}.",
            "top_institutions": top_institutions,
            "average_employment_rate": avg_rate,
            "median_salary": median_salary,
            "trend": trend,
            "data_quality": f"Based on {len(df)} records from {df['data_source'].nunique()} sources",
            "last_updated": df["last_updated"].iloc[0] if "last_updated" in df.columns else "Unknown"
        }

    def summarize_outcomes(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        """Enhanced outcome summarization with Gemini-powered insights."""
        self._load_data()  # Ensure fresh data
        matches = self.retriever.query(question, top_k=top_k)
        combined = "\n\n".join([m["text"] for m in matches])
        
        # Use Gemini summarization if available, otherwise fallback to offline
        if settings.online_mode:
            summary = gemini_summarize(combined, question)
        else:
            summary = offline_summarize(combined, max_sentences=8)
        
        # Add contextual insights based on current data
        if "employment" in question.lower() or "job" in question.lower():
            recent_employment = self.employment_df[self.employment_df["year"] == self.employment_df["year"].max()]
            if not recent_employment.empty:
                avg_rate = recent_employment["employment_rate"].mean()
                top_field = recent_employment.groupby("degree")["employment_rate"].mean().idxmax()
                summary += f"\n\nCurrent market data shows {avg_rate:.1f}% average employment rate, with {top_field} leading at {recent_employment[recent_employment['degree']==top_field]['employment_rate'].mean():.1f}%."
        
        if "salary" in question.lower() or "income" in question.lower():
            recent_salary = self.salary_df[self.salary_df["year"] == self.salary_df["year"].max()]
            if not recent_salary.empty:
                median_salary = recent_salary["median_salary"].median()
                top_paying_field = recent_salary.groupby("degree")["median_salary"].mean().idxmax()
                summary += f"\n\nCurrent salary data shows median of ₹{median_salary:,.0f}, with {top_paying_field} graduates earning the highest median salary."
        
        return {
            "question": question, 
            "summary": summary, 
            "sources": [m["meta"]["source"] for m in matches],
            "confidence": "High" if len(matches) >= 3 else "Medium",
            "data_freshness": "Real-time" if self.use_real_data else "Static",
            "llm_enabled": settings.online_mode,
            "processing_method": "Gemini-powered" if settings.online_mode else "Statistical analysis"
        }

    def compare_institutions(self, a: str, b: str, year: int | None = None) -> Dict[str, Any]:
        """Enhanced institution comparison with detailed metrics."""
        self._load_data()  # Ensure fresh data
        df = self.employment_df.copy()
        df_ab = df[df["institution"].str.lower().isin([a.lower(), b.lower()])]
        
        if year:
            df_ab = df_ab[df_ab["year"] == int(year)]
            
        if df_ab.empty:
            return {
                "summary": f"No matching data found for {a} vs {b} comparison.",
                "comparison": [],
                "recommendation": "Try different institutions or years."
            }
        
        # Enhanced comparison metrics with NaN/Inf handling
        comp = df_ab.groupby(["institution"]).agg({
            "employment_rate": ["mean", "std", "count"],
            "median_salary": ["mean", "std"]
        }).reset_index()
        
        # Flatten column names
        comp.columns = ["institution", "avg_employment_rate", "employment_std", "employment_count", 
                       "avg_salary", "salary_std"]
        
        # Handle NaN and Inf values
        for col in ["avg_employment_rate", "employment_std", "avg_salary", "salary_std"]:
            comp[col] = comp[col].replace([float('inf'), float('-inf')], 0)
            comp[col] = comp[col].fillna(0)
        
        # Convert to dict and clean values
        out = comp.to_dict(orient="records")
        for item in out:
            for key, value in item.items():
                if isinstance(value, float):
                    if pd.isna(value) or value == float('inf') or value == float('-inf'):
                        item[key] = 0
                    else:
                        item[key] = round(value, 2)
        
        # Calculate winner
        if len(out) == 2:
            inst_a_data = next((r for r in out if r["institution"].lower() == a.lower()), None)
            inst_b_data = next((r for r in out if r["institution"].lower() == b.lower()), None)
            
            if inst_a_data and inst_b_data:
                emp_winner = a if inst_a_data["avg_employment_rate"] > inst_b_data["avg_employment_rate"] else b
                salary_winner = a if inst_a_data["avg_salary"] > inst_b_data["avg_salary"] else b
                
                summary = f"Comparison of {a} vs {b}: {emp_winner} leads in employment rate ({inst_a_data['avg_employment_rate']:.1f}% vs {inst_b_data['avg_employment_rate']:.1f}%), while {salary_winner} leads in salary (₹{inst_a_data['avg_salary']:,.0f} vs ₹{inst_b_data['avg_salary']:,.0f})."
            else:
                summary = f"Comparison data available for {len(out)} institutions."
        else:
            summary = f"Comparison data available for {len(out)} institutions."
        
        return {
            "comparison": out, 
            "summary": summary,
            "data_quality": f"Based on {df_ab['data_source'].nunique()} data sources",
            "last_updated": df_ab["last_updated"].iloc[0] if "last_updated" in df_ab.columns else "Unknown"
        }

    def support_services_index(self) -> List[Dict[str, Any]]:
        """Enhanced support services analysis with detailed metrics."""
        self._load_data()  # Ensure fresh data
        rows: List[Dict[str, Any]] = []
        
        for _, r in self.support_df.iterrows():
            services = r.get("services", []) if isinstance(r.get("services"), list) else []
            score = score_support_index(services)
            
            # Enhanced metrics
            career_rating = r.get("career_services_rating", 0)
            alumni_strength = r.get("alumni_network_strength", 0)
            data_source = r.get("data_source", "Unknown")
            last_updated = r.get("last_updated", "Unknown")
            
            rows.append({
                "institution": r.get("institution"),
                "services": services,
                "support_index": score,
                "career_services_rating": round(career_rating, 1),
                "alumni_network_strength": round(alumni_strength, 1),
                "total_services": len(services),
                "data_source": data_source,
                "last_updated": last_updated
            })
        
        return sorted(rows, key=lambda x: x["support_index"], reverse=True)

    def roi_estimate(self, institution: str, degree: str, tuition_total: float, years: int = 4) -> Dict[str, Any]:
        """Enhanced ROI calculation with comprehensive financial analysis."""
        self._load_data()  # Ensure fresh data
        df = self.salary_df.copy()
        f = (df["institution"].str.lower() == institution.lower()) & (df["degree"].str.lower() == degree.lower())
        sub = df[f]
        
        if sub.empty:
            return {
                "summary": f"No salary data available for {institution} - {degree} combination.",
                "recommendation": "Try different institution or degree combinations."
            }
        
        # Enhanced ROI calculations with NaN/Inf handling
        median_salary = sub["median_salary"].median()
        employment_rate = sub["employment_rate"].median()
        
        # Clean values
        median_salary = 0 if pd.isna(median_salary) or median_salary == float('inf') or median_salary == float('-inf') else float(median_salary)
        employment_rate = 0 if pd.isna(employment_rate) or employment_rate == float('inf') or employment_rate == float('-inf') else float(employment_rate)
        
        salary_25th = sub["salary_percentile_25"].median() if "salary_percentile_25" in sub.columns else median_salary * 0.8
        salary_75th = sub["salary_percentile_75"].median() if "salary_percentile_75" in sub.columns else median_salary * 1.3
        
        # Clean percentile values
        salary_25th = 0 if pd.isna(salary_25th) or salary_25th == float('inf') or salary_25th == float('-inf') else float(salary_25th)
        salary_75th = 0 if pd.isna(salary_75th) or salary_75th == float('inf') or salary_75th == float('-inf') else float(salary_75th)
        
        expected_income_first_year = median_salary * (employment_rate / 100.0)
        years_to_break_even = tuition_total / max(expected_income_first_year, 1.0)
        
        # Calculate 5-year and 10-year projections
        salary_growth_rate = 0.03  # 3% annual growth
        income_5_year = expected_income_first_year * ((1 + salary_growth_rate) ** 5 - 1) / salary_growth_rate
        income_10_year = expected_income_first_year * ((1 + salary_growth_rate) ** 10 - 1) / salary_growth_rate
        
        # ROI percentage with NaN/Inf handling
        roi_5_year = ((income_5_year - tuition_total) / tuition_total) * 100 if tuition_total > 0 else 0
        roi_10_year = ((income_10_year - tuition_total) / tuition_total) * 100 if tuition_total > 0 else 0
        
        # Clean ROI values
        roi_5_year = 0 if pd.isna(roi_5_year) or roi_5_year == float('inf') or roi_5_year == float('-inf') else roi_5_year
        roi_10_year = 0 if pd.isna(roi_10_year) or roi_10_year == float('inf') or roi_10_year == float('-inf') else roi_10_year
        
        # Risk assessment
        risk_level = "Low" if employment_rate > 85 and median_salary > 70000 else "Medium" if employment_rate > 75 else "High"
        
        return {
            "institution": institution,
            "degree": degree,
            "median_salary": int(round(median_salary, 0)),
            "salary_range": f"₹{int(salary_25th):,} - ₹{int(salary_75th):,}",
            "employment_rate": round(employment_rate, 1),
            "expected_income_first_year": int(round(expected_income_first_year, 0)),
            "estimated_years_to_break_even": round(years_to_break_even, 1),
            "roi_5_year": round(roi_5_year, 1),
            "roi_10_year": round(roi_10_year, 1),
            "risk_level": risk_level,
            "data_quality": f"Based on {len(sub)} records from {sub['data_source'].nunique()} sources",
            "last_updated": sub["last_updated"].iloc[0] if "last_updated" in sub.columns else "Unknown"
        }

    # ---------- Parent-focused report ----------
    def parent_focused_summary(self, degree: str | None = None, year: int | None = None) -> str:
        """Enhanced parent-focused summary with actionable insights."""
        self._load_data()  # Ensure fresh data
        emp = self.analyze_employment(degree=degree, year=year)
        bullets = []
        
        if emp.get("average_employment_rate") is not None:
            bullets.append(f"Average employment rate is {emp['average_employment_rate']}% for {degree or 'all degrees'} in {year or 'recent years'}.")
        
        if emp.get("median_salary"):
            bullets.append(f"Median starting salary is ₹{emp['median_salary']:,}, providing strong earning potential.")
        
        if emp.get("trend"):
            trend_advice = "This is a growing field with excellent prospects." if emp["trend"] == "improving" else "Consider the long-term market outlook."
            bullets.append(f"Employment trend is {emp['trend']}. {trend_advice}")
        
        if emp.get("top_institutions"):
            top_names = ", ".join([r["institution"] for r in emp["top_institutions"][:3]])
            bullets.append(f"Top-performing institutions: {top_names}.")
        
        # Add support services insights
        support_data = self.support_services_index()
        if support_data:
            top_support = support_data[0]
            bullets.append(f"Best support services: {top_support['institution']} offers {top_support['total_services']} services with {top_support['support_index']} support index.")
        
        bullets.append("Key factors for success: early career planning, strong alumni networks, and internship experience.")
        bullets.append("Consider both employment rate and long-term career growth potential when making decisions.")
        
        # Create context for LLM synthesis
        context = f"Analysis for {degree or 'all degrees'} in {year or 'recent years'}"
        
        # Use Gemini synthesis if available, otherwise fallback to offline
        if settings.online_mode:
            return gemini_synthesize_insights(bullets, context)
        else:
            return synthesize_parent_friendly_insights(bullets)


def get_service(use_real_data: bool = True) -> AgentService:
    # Basic singleton pattern per process
    global _SERVICE
    try:
        return _SERVICE
    except NameError:
        _SERVICE = AgentService(use_real_data=use_real_data)
        return _SERVICE
