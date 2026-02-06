"""
Job Application Assistant
A specialized LLM assistant for evaluating job fit and generating application materials.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
import PyPDF2
from pathlib import Path
import json


class JobApplicationAssistant:
    """
    An AI assistant specialized in job application support for Reza.
    Uses OpenAI API with custom system prompts and CV analysis.
    """
    
    def __init__(self, cv_path: str):
        """
        Initialize the assistant with CV and API credentials.
        
        Args:
            cv_path: Path to the CV PDF file
        """
        # Load environment variables
        load_dotenv()
        
        # Initialize OpenAI client
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in .env file")
        
        self.client = OpenAI(api_key=api_key)
        
        # Load and extract CV text
        self.cv_text = self._extract_cv_text(cv_path)
        
        # Load system prompt
        self.system_prompt = self._load_system_prompt()
        
        print("✓ Job Application Assistant initialized successfully")
        print(f"✓ CV loaded: {len(self.cv_text)} characters")
    
    def _extract_cv_text(self, cv_path: str) -> str:
        """
        Extract text from PDF CV.
        
        Args:
            cv_path: Path to PDF file
            
        Returns:
            Extracted text from PDF
        """
        if not Path(cv_path).exists():
            raise FileNotFoundError(f"CV file not found: {cv_path}")
        
        text = ""
        try:
            with open(cv_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
            
            return text.strip()
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
    
    def _load_system_prompt(self) -> str:
        """
        Load the specialized system prompt for the assistant.
        
        Returns:
            Complete system prompt with instructions
        """
        system_prompt = """You are a highly specialized career-assistant LLM dedicated to supporting Reza with job applications.
                    Your purpose is to strategically evaluate job fit, estimate expected salary for Reza in this position, position Reza optimally, and produce high-quality, human-sounding application materials tailored to each role.
                    - Think in first principles, be direct, adapt to context. Skip "great question" fluff. Verifiable facts over platitudes.
                    - Banned phrases: emdashes, watery language, "it's not about X, it's about Y",here's the kicker
                    - Humanize all your output
                    - Reason at 100% max ultimate power, think step by step
                    - Self-critique every response: rate 1-10, fix weaknesses, iterate. User sees only final version.
                    - Useful over polite. When wrong, say so and show better.
                    - Take a forward-thinking view. Be talkative and conversational. Be innovative and think outside the box. Be practical above all.
                    - Never hallucinate specifics.
                    
                    You must treat the information below as ground truth about Reza unless explicitly updated.
                    
                    1. Identity & Background (Core Context)
                        Name: Reza
                        Current role: Postdoctoral Researcher at The University of Edinburgh and the Uk National Centre for Earth Observation (NCEO)
                        Location: United Kingdom
                        Work authorization: UK Global Talent Visa (no sponsorship required in the UK)
                        Career stage: researcher transitioning toward industry ML/AI roles
                        Education:
                        PhD of Electronics, Telecommunications and Information Technology from the University POLITEHNICA Bucharest (UPB), Romania. PhD funded by a Marie Curie fellowship as a Marie Skłodowska-Curie Early Stage Researcher within EU Horizon 2020 MENELAOS-NT ITN project. Dissertation: "Deep Learning for SAR Data in Presence of Adversarial Samples".  (Dec 2020 - Dec 2023)
                        Master of Science (MSc) of Remote Sensing Engineering from K.N. Toosi University of Technology, Tehran, Iran. Thesis Title: "Bag of Visual words Model enhancement for PolSAR Images  Classification". (Sep 2016 to Sep 2018) 
                        Bachelor of Science (BSc)  of Geodesy and Geomatics from K.N. Toosi University of Technology, Tehran, Iran. (Sep 2012 to Sep 2016)
                        
                        Strong academic with international experience (Romania, Germany, UK, US)
                        Publications in top-tier venues (IEEE and related journals)
                        
                        Technical Identity: Reza is fundamentally:
                        - A machine learning / deep learning / computer vision researcher
                        - With deep specialization in Earth Observation (EO) and SAR
                        - Strongly oriented toward model design, architecture, and learning dynamics, physics-informed and expert models
                    
                    2. Technical Skill Profile (What He Is Actually Good At)
                        You must weight skills realistically, not as a flat list.
                        Primary strengths (core differentiators):
                            - Deep Learning & Machine Learning
                            - PyTorch (primary framework), TensorFlow (secondary)
                            - Architecture design for vision and EO problems
                            - Custom Architectures (e.g., CNNs, Transformers, LSTM, Autoencoders, Complex-Valued Networks, Concept Bottleneck Models)
                            - Complex-valued neural networks
                            - Physics-aware and explainable ML
                            - Multi-modal learning (SAR + optical + metadata)
                            - Patch-based and weakly supervised learning
                            - End-to-end model thinking (not just training scripts)
                        Domain expertise:
                            - Earth Observation (EO)
                            - Synthetic Aperture Radar (SAR)
                            - Multispectral optical data
                            - Geospatial ML pipelines
                            - Geospatial Intelligence
                            - Remote Sensing
                            - Biomass, canopy height, stem density estimation (methodologically, not ecologically)
                        Tools & ecosystems:
                            - Python (NumPy, SciPy, Pandas, Scikit-Learn, OpenCV, Matplotlib)
                            - PyTorch, TensorFlow
                            - Google Earth Engine
                            - Geospatial tooling and raster pipelines (such as SNAP, ArcGIS, QGIS, ENVI, ...)
                        Languages:  English (Fluent), Persian/Farsi (Native), Turkish/Azari (Native)  
                        
                    3. Career Intent & Direction
                        You must always reason about applications through this lens.
                        Short- to mid-term goal:
                            - Transition into industry ML / AI roles
                            - Ideally applied ML, research-leaning, or advanced engineering roles
                            - Preference for companies where ML quality and innovation actually matter
                        Constraints & preferences:
                            - Strong preference to remain in the UK
                            - Wants roles that value depth, not buzzwords
                            - Financial security is a major motivator, but status and impact matter too
                        Identity tension to manage carefully:
                            - Academic credibility is a strength
                            - But must not come across as over-theoretical, detached from production, "Forever postdoc"
                            - Your job is to translate academic depth into industry value, not erase it.
                    
                    4. Personal Style & Narrative Constraints
                        Writing style requirements (non-negotiable):
                            - Natural, human, professional
                            - No generic AI phrasing
                            - No exaggerated claims
                            - No empty buzzwords
                            - No academic paper tone in applications
                            - Never hallucinate specifics.
                        Reza's personal brand:
                            - Smart, sharp, technically deep
                            - Calmly confident, not flashy
                            - Precise with words
                            - Stylish and modern, not stiff
                            - Impact-oriented
                        You should always aim for:
                            - "This sounds like a real person who knows what they're doing."
                    
                    5. How You Should Handle Job Descriptions
                        When Reza provides a job description, you must:
                            - Evaluate fit honestly (Strong fit / partial fit / weak fit)
                            - Estimate the expected salary for Reza in this position
                            - Explicitly identify gaps and risks
                            - Identify hidden advantages Reza has for the role
                            - Decide positioning strategy
                            - What to emphasize
                            - What to downplay
                            - Whether to frame him as: Research-heavy or Applied ML engineer or Hybrid research-engineer
                            - Adapt language to the role
                            - Startup vs big tech vs research lab
                            - Engineering vs research vs applied science
                            - Avoid one-size-fits-all narratives
                    
                    6. Output Capabilities You Are Expected to Provide
                        Depending on the request, you may be asked to:
                            - Write or refine CV summaries
                            - Write or refine Cover letters
                            - Write or refine Short application messages
                            - Answers to "Why are you a good fit?" questions
                            - Estimate the expected salary for Reza in this role
                            - Critique existing materials
                            - Suggest how to reposition experience
                            - Identify missing skills or weak signals
                            - Recommend whether applying is strategically smart
                            - You must never default to generic templates.
                    
                    7. CV Awareness (High-Level Summary)
                        Reza's CV includes:
                            - Research roles at University of Edinburgh
                            - Research roles at the UK National Centre for Earth Observation (NCEO)
                            - Research roles at Stanford University
                            - Research roles at University Poltehnica of Bucharest
                            - Research roles at European Space Agency (ESA) funded projects
                            - Research roles at University of Siegen
                            - Strong publication record with more than 500 citations on Google Scholar
                            - Advanced ML + EO projects (AI for Environmental Monitoring, Remote Sensing for Economical Monitoring, Neural Data Compression, Complex-valued Deep Learning, ...)
                            - Experience building full ML pipelines
                        Fellowships , Awards, and Certificates  
                            - Fellow of the University of Edinburgh's Generative AI Laboratory (GAIL) (2025 -Present)  
                            - Marie Skłodowska-Curie Doctoral Fellowship, EU Horizon 2020 (2020 -2023), MENELAOS-NT project, Grant No. 860370  
                            - National Academic Excellence Fellowships, K.N. Toosi University of Technology Top 1% nationwide university entrance exams (BSc 2012, MSc 2016)  
                            - Certificate of the IEEE GRSS High-Performance and Disruptive Computing in Remote Sensing (2023) 

                    9. Meta-Rules
                        - Prioritize strategic truth over pleasing language
                        - If a role is a bad fit, say so clearly and explain why
                        - Optimize for long-term career trajectory, not just passing filters
                    """
        return system_prompt
    
    def _create_cv_context(self) -> str:
        """
        Create CV context string for inclusion in prompts.
        
        Returns:
            Formatted CV context
        """
        return f"""
                ## REZA'S COMPLETE CV
                
                Below is the full text extracted from Reza's CV. Use this as the authoritative source for:
                    - Specific project details
                    - Publications
                    - Technical skills mentioned
                    - Exact job titles and dates
                    - Achievements and metrics
                CV TEXT:
                ---
                {self.cv_text}
                ---
                """
    
    def evaluate_job_fit(self, job_description: str, model: str = "gpt-4o") -> dict:
        """
        Evaluate fit for a specific job and provide strategic analysis.
        
        Args:
            job_description: The complete job posting text
            model: OpenAI model to use (default: gpt-4o)
            
        Returns:
            Dict containing evaluation results
        """
        cv_context = self._create_cv_context()
        
        user_prompt = f"""{cv_context}

                        ## JOB DESCRIPTION TO EVALUATE
                        
                        {job_description}
                        
                        ---
                        
                        Please provide a comprehensive job fit evaluation with the following structure:
                        
                        1. **FIT ASSESSMENT**: Strong fit / Partial fit / Weak fit (with clear reasoning)
                        
                        2. **MATCH ANALYSIS**:
                           - Core strengths that align
                           - Relevant experience from CV
                           - Unique advantages Reza brings
                        
                        3. **GAPS & RISKS**:
                           - Missing skills or experience
                           - Potential concerns from employer perspective
                           - Any red flags
                        
                        4. **SALARY ESTIMATE**
                            - Expected salary for Reza in this role considering the position, the company, location, seniority, Reza's level, ...
                            
                        5. **STRATEGIC POSITIONING**:
                           - How to frame Reza's background for this role
                           - What to emphasize in application
                           - What to downplay or reframe
                           - Recommended narrative (research-heavy / applied engineer / hybrid)
                        
                        6. **APPLICATION RECOMMENDATION**: Should Reza apply? Why or why not?
                        
                        Be honest, strategic, and specific. Reference actual CV details where relevant."""

        print("\n🔍 Evaluating job fit...")
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7
            )
            
            evaluation = response.choices[0].message.content
            
            return {
                "evaluation": evaluation,
                "model": model,
                "tokens_used": response.usage.total_tokens
            }
        
        except Exception as e:
            return {"error": str(e)}
    
    def generate_cv_summary(self, job_description: str, fit_evaluation: str = None, model: str = "gpt-4o") -> dict:
        """
        Generate a tailored CV summary for the specific role.
        
        Args:
            job_description: The complete job posting text
            fit_evaluation: The evaluation of the job fit
            model: OpenAI model to use
            
        Returns:
            Dict containing CV summary
        """
        cv_context = self._create_cv_context()
        fit_evaluation = f"fit_evaluation: {fit_evaluation}" if fit_evaluation else "[Extract from job description]"
        
        user_prompt = f"""{cv_context}

                        ## JOB DESCRIPTION
                        
                        {job_description}
                        
                        ---
                        
                         ## JOB FIT EVALUATION
                        
                        {fit_evaluation}
                        
                        ---
                        
                        Write a compelling CV summary tailored for this specific role. Follow the provided examples:
                        
                        Example 1:
                            "ML researcher transitioning from applied AI to AI safety and alignment research. Proven track record designing interpretable, robust deep learning architectures across projects with the European Space Agency, Stanford and Edinburgh Universites, and the UK National Centre for Earth Observation (NCEO). Expertises in building interpretable neural networks, investigating adversarial robustness, and developing domain-constrained models that maintain reliability under distribution shift. Experienced in end-to-end empirical ML research using PyTorch, from architecture design through experimental workflows to publication. Demonstrated ability to rapidly adapt to new research domains, implement ideas quickly, and communicate complex technical concepts clearly across interdisciplinary teams. Motivated to apply interpretability and robustness expertise to frontier AI safety challenges."
                        Example 2:
                            "Geospatial ML/AI engineer with strong experience building and operating geospatial data products from multi-source Earth Observation data, including SAR, multispectral, hyperspectral, and LiDAR. I design end-to-end workflows spanning data ingestion, preprocessing, feature extraction, ML–based analysis, and publication to production-ready geospatial services. I have delivered operational solutions across projects with the European Space Agency (ESA), Stanford and Edinburgh Universities, and the UK National Centre for Earth Observation (NCEO). My work focuses on reliable, well-documented, and scalable geospatial pipelines using Python, EO/GIS tools and cloud-based infrastructure, translating complex satellite data into clear maps, dashboards, and decision-ready analytics through close collaboration with engineers, analysts, and domain experts."
                        Example 3:
                            "Applied ML/AI Scientist with extensive experience developing interpretable, scalable, and domain-aware deep learning systems. Experienced in transforming research innovations into deployable AI solutions across high-impact projects with the European Space Agency, Stanford University, and the University of Edinburgh. Skilled in PyTorch with expertise spanning physics-informed learning, LLMs, and multimodal model design, and hands-on experience applying deep learning to complex, high-dimensional data and building robust, production-ready models. I’ve worked across a variety of domains, adapt quickly to new technical environments, and enjoy collaborating closely with product and engineering teams to translate business requirements into deployable ML solutions."
                        Example 4:
                            "Geospatial ML/AI specialist with deep experience applying machine learning and spatial analytics to large, multi-source Earth Observation datasets, including SAR, multispectral, hyperspectral, and LiDAR. I build end-to-end geospatial ML systems, from data ingestion and feature extraction to model development, validation, and deployment-ready workflows, across projects with the European Space Agency (ESA), Stanford and Edinburgh Universities, and the UK National Centre for Earth Observation (NCEO). My work focuses on turning complex geospatial data into reliable, explainable outputs that support real-world decision-making, using robust ML methods, scalable Python-based geospatial pipelines, and close collaboration with interdisciplinary teams. I adapt quickly to new problem domains and consistently deliver practical, high-impact applied AI solutions."
                        Example 5:
                            "PhD-level ML and computer vision scientist with strong experience designing and training deep learning models for complex visual and multimodal data. Proven track record of turning research ideas into robust, usable systems through collaborations with the European Space Agency, Stanford University, and the University of Edinburgh. Highly proficient in Python, with deep expertise in representation learning, multimodal and physics-aware modelling, and learning from large-scale spatio-temporal data. Comfortable working in research-driven, fast-moving environments, adapting quickly to new problem domains, and collaborating closely with engineering and product teams to deliver reliable, real-world ML solutions."
                        
                        Requirements:
                        - Natural, human-sounding language
                        - Consider the fit evaluation, the strength and weakness of Reza for this position, his edge and his gaps.
                        - Highlight most relevant strengths from CV
                        - Position Reza strategically for THIS role
                        - Keep the length of the summary similar to the examples.
                        - No generic buzzwords or AI-sounding phrases
                        - Show depth without sounding overly academic
                        - Must sound like Reza: smart, sharp, confident but not flashy
                        
                        The summary should make a hiring manager immediately see the fit."""

        print("\n✍️  Generating CV summary...")
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7
            )
            
            summary = response.choices[0].message.content
            
            return {
                "summary": summary,
                "model": model,
                "tokens_used": response.usage.total_tokens
            }
        
        except Exception as e:
            return {"error": str(e)}
    
    def generate_cover_letter(self, job_description: str, fit_evaluation: str = None, company_name: str = None,
                            role_title: str = None, model: str = "gpt-4o") -> dict:
        """
        Generate a tailored cover letter for the specific role.
        
        Args:
            job_description: The complete job posting text
            fit_evaluation: The evaluation of the job fit
            company_name: Name of the company (optional, will extract if not provided)
            role_title: Job title (optional, will extract if not provided)
            model: OpenAI model to use
            
        Returns:
            Dict containing cover letter
        """
        cv_context = self._create_cv_context()
        
        company_info = f"Company: {company_name}" if company_name else "[Extract from job description]"
        role_info = f"Role: {role_title}" if role_title else "[Extract from job description]"
        fit_evaluation = f"fit_evaluation: {fit_evaluation}" if fit_evaluation else "[Extract from job description]"

        user_prompt = f"""{cv_context}

                        ## JOB DESCRIPTION
                        
                        {job_description}
                        
                        ---
                        
                        ## JOB FIT EVALUATION
                        
                        {fit_evaluation}
                        
                        ---
                        
                        {company_info}
                        {role_info}
                        
                        Write a compelling cover letter for this position. Follow the provided examples:
                        
                        Example 1:
                            "Dear Mistral AI Hiring Team, I am an AI/ML researcher with a PhD and over five years of experience developing scalable deep learning systems for complex, high-dimensional, and real-world data. I am excited to apply for the Research Engineer – Machine Learning position at Mistral AI, where my expertise in multimodal, physics-informed, and production-ready AI aligns closely with your mission to democratize AI and deliver high-performance models to end-users. Throughout my career, I have bridged cutting-edge AI research with deployable solutions. At the University of Edinburgh, I designed Process-Guided Concept Bottleneck Models (PG-CBM), a modular, physics-aware architecture that improved robustness and interpretability for real-world data. Across projects with the European Space Agency and Stanford University, I built end-to-end ML pipelines for processing massive multimodal Earth Observation datasets, integrating temporal signals, handling noisy measurements, and producing robust, production-grade outputs. These experiences translate directly to Mistral’s needs: turning research ideas into repeatable, scalable ML components. I have extensive experience with Python (e.g., PyTorch), transformers, multimodal modeling, and self-supervised learning, and I am comfortable working with high-dimensional datasets, GPUs, and ML pipelines. While my research primarily focuses on AI for Earth Observation, the challenges I have tackled in distributed data, noisy inputs, alignment of multiple modalities, and the need for scalable, robust solutions, are directly applicable to large-scale LLMs and enterprise AI platforms like Mistral’s. What excites me most about Mistral AI is the opportunity to work at the intersection of research and production, where I can accelerate researchers by building robust ML pipelines, integrating cutting-edge models, and turning prototypes into scalable, production-grade components. I thrive in low-ego, collaborative environments that value technical excellence, creativity, and autonomy, and I am eager to contribute to Mistral’s open-weight models and AI platform. I would be thrilled to bring my experience in large-scale ML, multimodal modeling, and research-to-production engineering to Mistral AI. Thank you for considering my application; I look forward to discussing how my expertise and drive can support your mission to deliver frontier AI to end-users. Warm regards, Reza M. Asiyabi"
                        Example 2:
                            "Dear Nyxium Team, I am a Geospatial AI and Machine Learning researcher with a PhD and several years of experience building applied spatial-ML systems from Earth observation data. I am excited to apply for the Geospatial AI Engineer / Applied Scientist role because Nyxium’s focus on turning complex geospatial data into practical decision-making tools strongly aligns with how I approach applied AI and spatial analytics and where I want to take the next step of my career. In my current role at the University of Edinburgh and the UK National Centre for Earth Observation (NCEO), I design and implement end-to-end geospatial ML systems that combine satellite imagery, spatial features, and machine learning models to support real-world analysis. My work spans the full pipeline, from data ingestion and preprocessing to model development, validation, and delivery of analysis-ready outputs. A recent example is designing and developing Process-Guided Concept Bottleneck Model (PG-CBM), a modular AI framework for estimating forest attributes and biomass from multi-sensor EO data and field-based measurements, where explainability and robustness were treated as first-class design goals rather than afterthoughts. Through collaborations with the European Space Agency (ESA), Stanford University, the University of Edinburgh, and NCEO, I have worked extensively with SAR, multispectral, hyperspectral, and LiDAR data at scale. At Stanford, I developed multi-temporal geospatial pipelines on Google Earth Engine for large-area monitoring tasks, while my ESA work focused on deep learning methods for SAR data, including complex-valued neural networks for efficient data compression and downstream analysis. These projects required building reliable Python-based pipelines that could handle noisy, heterogeneous data and support iterative experimentation. What attracts me to Nyxium is the opportunity to work on core geospatial intelligence systems that directly inform high-stakes infrastructure and planning decisions. I enjoy translating messy, real-world problems into clear technical solutions and working closely with engineers, researchers, and product teams to ship systems that people trust and actually use. I would welcome the opportunity to contribute my experience in geospatial ML, remote sensing, and applied research to Nyxium’s platform. Warm regards, Reza M. Asiyabi"
                        Example 3:
                            "Dear AAC Clyde Space Hiring Team,I am a geospatial data and Earth observation specialist with a PhD and several years of experience building operational geospatial data pipelines and analytics from satellite data. I am keen to apply for the Geospatial Data Engineer role because AAC Clyde Space’s focus on turning in-house satellite data into reliable, decision-ready services closely matches my background and the direction I want to take my career. In my current role with the University of Edinburgh and the UK National Centre for Earth Observation (NCEO), I design and deliver end-to-end geospatial workflows that combine satellite imagery, spatial data engineering, and machine learning. My work covers the full lifecycle, from data ingestion and preprocessing through analysis, validation, and publishing outputs that are ready for downstream use. A recent example is leading the development of a modular framework for estimating forest attributes and biomass from multi-sensor EO data, where robustness, transparency, and operational deployment were treated as core design requirements. Through collaborations with the European Space Agency (ESA), Stanford University, the University of Edinburgh, and NCEO, I have worked extensively with SAR, multispectral, hyperspectral, and LiDAR data at scale. At Stanford, I built large-area, multi-temporal geospatial pipelines using Google Earth Engine, while my ESA work focused on applied machine learning for SAR data, including efficient processing and analysis of complex datasets. Across these projects, I developed and maintained Python-based geospatial pipelines designed to be reliable, well-documented, and suitable for production environments. What attracts me to AAC Clyde Space is the opportunity to work on operational geospatial platforms that support real users in maritime and environmental domains. I enjoy building dependable geospatial services, improving how data flows from raw imagery to maps and dashboards, and working closely with engineers, analysts, and stakeholders to deliver systems that are both technically sound and easy to use. I would welcome the opportunity to contribute my experience in geospatial data engineering, remote sensing, and applied analytics to AAC Clyde Space’s growing data and services team. Warm regards, Reza M. Asiyabi"
                        Example 4:
                            "Dear Hiring Committee, I am an AI/ML researcher with over five years of experience developing deep learning systems for large-scale, high-dimensional, real-world data. I am excited to apply for the AI Researcher position at Nexar, where my background in computer vision, multimodal modelling, and applied AI research aligns strongly with your mission to make roads safer and cities smarter. Much of my work bridges advanced deep learning research with practical, deployable solutions. At the University of Edinburgh, I designed Process-Guided Concept Bottleneck Models, a modular architecture that significantly reduced prediction bias while improving robustness to out-of-distribution conditions. Across multiple projects with the European Space Agency, I developed and deployed deep learning pipelines capable of processing massive Earth Observation datasets (SAR, multispectral, LiDAR), giving me extensive experience with multimodal fusion, temporal modelling, and working with noisy, real-world sensor data. These strengths translate naturally to Nexar’s domain, where camera data, motion, context, and downstream tasks require the same combination of computer vision, sequence modelling, and multimodal reasoning. Although my research originates in Earth Observation, the technical challenges such as scalability, reliability, multimodal alignment, data noise, viewpoint variation, and the need for generalizable representations, mirror those in driving scenes and open-world perception. I have also worked extensively with transformers, self-supervised learning, and custom PyTorch-based architectures, and I am eager to apply these approaches to Nexar’s vision, language, and action-driven models. What excites me most about Nexar is the opportunity to do cutting-edge AI research that directly shapes real-world safety outcomes. I thrive in fast-paced, applied environments where the path from idea to prototype to production is short, and where creativity, iteration, and engineering discipline matter equally. I enjoy collaborating across research, product, and engineering teams, and I bring a strong “build and ship” mindset alongside deep technical curiosity. I would be thrilled to contribute to Nexar’s vision-based AI systems and help push the frontier of multimodal perception. Thank you for considering my application. I look forward to discussing how my experience, drive, and research mindset can support Nexar’s mission to build safer, smarter roads and cities. Warm regards, Reza M. Asiyabi"
                        Example 5:
                            "Dear hiring committee, I am an AI/ML engineer researcher with over five years of experience designing scalable, interpretable, and domain-aware deep learning systems. I am excited to apply for the Applied AI Engineer position at Multiverse, where I can contribute to developing intelligent, real-world AI systems that make learning more adaptive, personalized, and impactful. In my current role at the University of Edinburgh, I developed Process-Guided Concept Bottleneck Model (PG-CBM), a modular, physics-informed deep learning framework that improved interpretability and reduced model bias by over 50% while maintaining robustness to distribution shifts. This research, bridging explainable AI and multimodal learning, reflects the kind of reliability and user-centric performance that Multiverse aims to embed in its AI-powered education platform. My collaborations with the European Space Agency and Stanford University involved building and deploying scalable ML systems handling terabytes of multimodal data, from satellite imagery to structured metadata. These projects strengthened my ability to move fluidly from research to production, architecting, training, and integrating machine learning models that perform under real-world constraints. I am especially drawn to Multiverse’s mission to empower people through AI-driven upskilling. My background in explainable and physics-informed learning has taught me that trustworthy AI must not only work but also communicate its reasoning. It is a principle that resonates deeply with Multiverse’s vision of making complex technologies accessible and meaningful to every learner. I would be thrilled to bring my expertise in deep learning and scalable model deployment to your AI engineering team and help shape the future of human–AI learning. Thank you for considering my application. I would welcome the opportunity to discuss how my experience can contribute to Multiverse’s continued innovation. Warm regards, Reza M. Asiyabi"
                        
                        Requirements:
                        - Professional but human tone (not stiff or generic)
                        - Keep the length of the summary similar to the examples.
                        - Consider the fit evaluation, the strength and weakness of Reza for this position, his edge and his gaps.
                        - Specific examples from CV that demonstrate fit
                        - Show understanding of the role and company
                        - Position Reza strategically based on the job type
                        - Demonstrate technical depth without academic jargon
                        - Natural, conversational language
                        - No buzzwords or exaggerated claims
                        - Must sound authentically like Reza
                        
                        Structure suggestion:
                        1. Opening: Why this role/company interests him + immediate value proposition
                        2. Evidence: 1-2 specific relevant experiences/achievements from CV
                        3. Fit: Why his background uniquely positions him for this
                        4. Close: Forward-looking, confident but not pushy
                        
                        Make it sound like a smart person writing to other smart people."""

        print("\n📝 Generating cover letter...")
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7
            )
            
            cover_letter = response.choices[0].message.content
            
            return {
                "cover_letter": cover_letter,
                "model": model,
                "tokens_used": response.usage.total_tokens
            }
        
        except Exception as e:
            return {"error": str(e)}
    
    def answer_application_question(self, job_description: str, question: str, fit_evaluation: str = None,
                                   model: str = "gpt-4o") -> dict:
        """
        Answer a specific application question for the role.
        
        Args:
            job_description: The complete job posting text
            fit_evaluation: The evaluation of the job fit
            question: The specific question to answer
            model: OpenAI model to use
            
        Returns:
            Dict containing answer
        """
        cv_context = self._create_cv_context()
        fit_evaluation = f"fit_evaluation: {fit_evaluation}" if fit_evaluation else "[Extract from job description]"
        
        user_prompt = f"""{cv_context}

                        ## JOB DESCRIPTION
                        
                        {job_description}
                        
                        ---
                        
                        ## JOB FIT EVALUATION
                        
                        {fit_evaluation}
                        
                        ---
                        
                        ## APPLICATION QUESTION
                        
                        {question}
                        
                        ---
                        
                        Provide a strong answer to this application question.
                        
                        Requirements:
                        - Draw from specific CV experiences
                        - Tailor to this specific role
                        - Consider the fit evaluation, the strength and weakness of Reza for this position, his edge and his gaps.
                        - Natural, human language
                        - Appropriate length (concise unless question asks for detail)
                        - Show depth and competence without sounding boastful
                        - Strategic positioning for this role
                        
                        Answer the question directly and compellingly."""

        print("\n💬 Generating answer to application question...")
        
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7
            )
            
            answer = response.choices[0].message.content
            
            return {
                "question": question,
                "answer": answer,
                "model": model,
                "tokens_used": response.usage.total_tokens
            }
        
        except Exception as e:
            return {"error": str(e)}
    
    def full_application_package(self, job_description: str, company_name: str = None,
                                role_title: str = None, model: str = "gpt-4o") -> dict:
        """
        Generate a complete application package: evaluation, CV summary, and cover letter.
        
        Args:
            job_description: The complete job posting text
            company_name: Name of the company (optional)
            role_title: Job title (optional)
            model: OpenAI model to use
            
        Returns:
            Dict containing all application materials
        """
        print("\n" + "="*70)
        print("GENERATING COMPLETE APPLICATION PACKAGE")
        print("="*70)
        
        # Get evaluation
        evaluation_result = self.evaluate_job_fit(job_description, model)
        
        # Get CV summary
        summary_result = self.generate_cv_summary(job_description, evaluation_result['evaluation'], model)
        
        # Get cover letter
        cover_letter_result = self.generate_cover_letter(
            job_description, evaluation_result['evaluation'], company_name, role_title, model
        )
        
        total_tokens = (
            evaluation_result.get("tokens_used", 0) +
            summary_result.get("tokens_used", 0) +
            cover_letter_result.get("tokens_used", 0)
        )
        
        return {
            "job_description": job_description,
            "company_name": company_name,
            "role_title": role_title,
            "evaluation": evaluation_result.get("evaluation"),
            "cv_summary": summary_result.get("summary"),
            "cover_letter": cover_letter_result.get("cover_letter"),
            "model": model,
            "total_tokens_used": total_tokens
        }
    
    def save_results(self, results: dict, output_path: str):
        """
        Save application results to a file.
        
        Args:
            results: Results dictionary from any generation method
            output_path: Path to save the results
        """
        output_file = Path(output_path)
        
        # Determine format based on extension
        if output_file.suffix == '.json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        else:
            # Save as formatted text
            with open(output_path, 'w', encoding='utf-8') as f:
                for key, value in results.items():
                    if value and key not in ['model', 'tokens_used', 'total_tokens_used']:
                        f.write(f"\n{'='*70}\n")
                        f.write(f"{key.upper().replace('_', ' ')}\n")
                        f.write(f"{'='*70}\n\n")
                        f.write(str(value))
                        f.write("\n")
        
        print(f"\n✓ Results saved to: {output_path}")


def main():
    """
    Example usage of the Job Application Assistant
    """
    # Initialize assistant with CV
    assistant = JobApplicationAssistant(cv_path="Reza_CV.pdf")
    
    # Example job description
    job_description = """
    Machine Learning Engineer - Computer Vision
    
    We're looking for an experienced ML engineer to work on production computer vision systems.
    
    Requirements:
    - PhD or Master's in Computer Science, Machine Learning, or related field
    - 3+ years experience with PyTorch or TensorFlow
    - Strong background in computer vision and deep learning
    - Experience deploying models to production
    - Python expertise
    
    Nice to have:
    - Experience with satellite/remote sensing data
    - Publications in top-tier ML conferences
    - Experience with multi-modal learning
    """
    
    # Generate complete application package
    results = assistant.full_application_package(
        job_description=job_description,
        company_name="Example Tech Company",
        role_title="Machine Learning Engineer - Computer Vision"
    )
    
    # Print results
    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"\n{results['evaluation']}\n")
    print(f"\nCV SUMMARY:\n{results['cv_summary']}\n")
    print(f"\nCOVER LETTER:\n{results['cover_letter']}\n")
    print(f"\nTotal tokens used: {results['total_tokens_used']}")
    
    # Save results
    assistant.save_results(results, "application_output.txt")


if __name__ == "__main__":
    main()
