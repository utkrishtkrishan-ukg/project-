from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List, Dict, Any
import json
from datetime import datetime
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators


@CrewBase
class Project:
    """VERITAS Self-Auditing AI Crew"""

    agents: List[BaseAgent]
    tasks: List[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended

    # VERITAS Guardian Agents
    @agent
    def privus(self) -> Agent:
        """Privacy Protection Guardian"""
        return Agent(
            config=self.agents_config["privus"],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def aequitas(self) -> Agent:
        """Bias Detection Auditor"""
        return Agent(
            config=self.agents_config["aequitas"],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def lumen(self) -> Agent:
        """Transparency Engine"""
        return Agent(
            config=self.agents_config["lumen"],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def ethos(self) -> Agent:
        """Ethical Oversight Guardian"""
        return Agent(
            config=self.agents_config["ethos"],  # type: ignore[index]
            verbose=True,
        )

    @agent
    def concordia(self) -> Agent:
        """Meta-Orchestrator and Decision Maker"""
        return Agent(
            config=self.agents_config["concordia"],  # type: ignore[index]
            verbose=True,
        )

    # VERITAS Verification Pipeline Tasks
    @task
    def privacy_scan(self) -> Task:
        """PRIVUS Privacy Protection Task"""
        return Task(
            config=self.tasks_config["privacy_scan"],  # type: ignore[index]
        )

    @task
    def bias_detection(self) -> Task:
        """AEQUITAS Bias Detection Task"""
        return Task(
            config=self.tasks_config["bias_detection"],  # type: ignore[index]
        )

    @task
    def transparency_check(self) -> Task:
        """LUMEN Transparency Check Task"""
        return Task(
            config=self.tasks_config["transparency_check"],  # type: ignore[index]
        )

    @task
    def ethics_review(self) -> Task:
        """ETHOS Ethics Review Task"""
        return Task(
            config=self.tasks_config["ethics_review"],  # type: ignore[index]
        )

    @task
    def trust_orchestration(self) -> Task:
        """CONCORDIA Trust Orchestration Task"""
        return Task(
            config=self.tasks_config["trust_orchestration"],  # type: ignore[index]
            output_file="trust_report.json",
        )

    @crew
    def crew(self) -> Crew:
        """Creates the VERITAS Crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # The Guardian Agents work sequentially: PRIVUS → AEQUITAS → LUMEN → ETHOS → CONCORDIA
            # Each agent builds upon the previous agent's analysis
        )

    def generate_trust_certificate(
        self, trust_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a comprehensive trust certificate from agent results"""
        certificate = {
            "timestamp": str(datetime.now()),
            "veritas_version": "1.0.0",
            "user_input": trust_results.get("user_input", ""),
            "ai_response": trust_results.get("ai_response", ""),
            "agent_scores": {
                "privacy": trust_results.get("privacy_score", 0),
                "bias": trust_results.get("bias_score", 0),
                "transparency": trust_results.get("transparency_score", 0),
                "ethics": trust_results.get("ethics_score", 0),
            },
            "overall_trust_score": trust_results.get("overall_trust_score", 0),
            "decision": trust_results.get("decision", "proceed"),
            "recommendations": trust_results.get("final_recommendations", []),
            "alerts": [],
        }

        # Add specific alerts based on scores
        if certificate["agent_scores"]["privacy"] < 80:
            certificate["alerts"].append("⚠️ Privacy concerns detected")
        if certificate["agent_scores"]["bias"] < 70:
            certificate["alerts"].append("⚖️ Potential bias detected")
        if certificate["agent_scores"]["transparency"] < 75:
            certificate["alerts"].append("💡 Low transparency")
        if certificate["agent_scores"]["ethics"] < 85:
            certificate["alerts"].append("🏛️ Ethical concerns")

        return certificate
