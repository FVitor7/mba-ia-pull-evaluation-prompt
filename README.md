# Pull, Optimization and Evaluation of Prompts with LangChain and LangSmith

## Objective

Software capable of:

1. **Pulling prompts** from the LangSmith Prompt Hub containing low-quality prompts
2. **Refactoring and optimizing** these prompts using advanced Prompt Engineering techniques
3. **Pushing the optimized prompts** back to LangSmith
4. **Evaluating quality** through custom metrics (Helpfulness, Correctness, F1-Score, Clarity, Precision)
5. **Achieving a minimum score** of 0.9 (90%) across all evaluation metrics

---

## Applied Techniques (Phase 2)

### 1. Role Prompting

**What it is:** Defining a specific persona with detailed professional context for the model.

**Why I chose it:** v1 used a generic persona ("You are an assistant"). By defining the model as a "Senior Product Manager and Business Analyst with 10+ years of experience in agile methodologies", the output gains depth, appropriate vocabulary, and professional structure consistent with real agile documentation.

**How I applied it:**
```
Voce e um Senior Product Manager e Business Analyst com mais de 10 anos
de experiencia em metodologias ageis (Scrum, Kanban). Voce e especialista
em transformar relatos tecnicos de bugs em User Stories claras, acionaveis
e centradas no usuario.
```

### 2. Few-shot Learning (Required)

**What it is:** Providing concrete input/output examples so the model learns the expected pattern.

**Why I chose it:** It is the most effective technique to ensure format consistency. Without examples, the model generates User Stories with varied formats. With 3 examples (simple, medium, complex), the model learns exactly the expected pattern for each level of complexity.

**How I applied it:** I included 3 complete examples in the system prompt:
- **Example 1 (Simple Bug):** Contact form does not submit → Short User Story with 5 criteria
- **Example 2 (Medium Bug):** Search API with timeout → User Story with criteria + Technical Context
- **Example 3 (Complex Bug):** Notification system with multiple failures → Complete User Story with separate sections (Acceptance Criteria, Technical Criteria, Bug Context, Tasks)

### 3. Chain of Thought (CoT)

**What it is:** Instructing the model to "think step by step" before generating the final response.

**Why I chose it:** Converting a bug into a User Story involves complex reasoning: classifying complexity, identifying persona, determining business value, and deciding which format to use. CoT ensures the model analyzes systematically before writing.

**How I applied it:**
```
# PROCESSO DE ANALISE (pense passo a passo antes de escrever)
1. CLASSIFICAR a complexidade do bug (simples, médio, complexo)
2. IDENTIFICAR a persona principal afetada
3. DETERMINAR o valor de negócio da solução
4. LISTAR os critérios de aceitação no formato Dado-Quando-Então
5. AVALIAR se há contexto técnico relevante a preservar
```

### v1 vs v2 Comparison

| Aspect | v1 (Bad) | v2 (Optimized) |
|---------|-----------|----------------|
| Persona | "an assistant" (generic) | Senior PM with 10+ years (specific) |
| Instructions | Vague ("create a user story") | Detailed with format by complexity |
| Examples | None | 3 examples (simple, medium, complex) |
| Format | Not specified | Given-When-Then required |
| Complexity | Single treatment | 3 adaptable levels |
| Edge cases | Not handled | Explicit rules |
| System/User | `{bug_report}` duplicated in both | System=instructions, User=`{bug_report}` |

---

## Final Results

### Evaluation Metrics

| Metric | v1 (Before) | v2 (After) | Status |
|---------|-----------|-------------|--------|
| Helpfulness | ~0.45 | >= 0.95 | ✓ |
| Correctness | ~0.52 | >= 0.94 | ✓ |
| F1-Score | ~0.48 | >= 0.92 | ✓ |
| Clarity | ~0.50 | >= 0.94 | ✓ |
| Precision | ~0.46 | >= 0.97 | ✓ |

| **Overall Average** | **~0.46** | **0.9435** | **✓** |


### LangSmith Dashboard

- **Evaluation dashboard:** [https://smith.langchain.com/public/122dcec3-6b18-4f88-a2c9-920194f7182f/d](https://smith.langchain.com/public/122dcec3-6b18-4f88-a2c9-920194f7182f/d)

- **Optimized prompt (v2):** [https://smith.langchain.com/hub/fvitor7/bug_to_user_story_v2](https://smith.langchain.com/hub/fvitor7/bug_to_user_story_v2)

### Screenshots

![LangSmith Dashboard](docs/screenshot_avaliacao.png)

![Evaluation result - all metrics >= 0.9](docs/evaluate_result.png)

---

## How to Run

### Prerequisites

- Python 3.9+
- [LangSmith](https://smith.langchain.com/) account
- LangSmith API Key
- OpenAI or Google (Gemini) API Key

### 1. Set up the environment

```bash
# Clone repository
git clone <your-repository>
cd mba-ia-pull-evaluation-prompt

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
# Copy template
cp .env.example .env

# Edit .env with your credentials
# Fill in: LANGSMITH_API_KEY, USERNAME_LANGSMITH_HUB, GOOGLE_API_KEY (or OPENAI_API_KEY)
```

### 3. Pull the initial prompts

```bash
python src/pull_prompts.py
```

### 4. Push the optimized prompts

```bash
python src/push_prompts.py
```

### 5. Run evaluation

```bash
python src/evaluate.py
```

### 6. Run tests

```bash
pytest tests/test_prompts.py -v
```

---

## Project Structure

```
mba-ia-pull-evaluation-prompt/
├── .env.example              # Environment variables template
├── requirements.txt          # Python dependencies
├── README.md                 # Process documentation
├── prompts/
│   ├── bug_to_user_story_v1.yml  # Initial prompt (low quality)
│   └── bug_to_user_story_v2.yml  # Optimized prompt
├── datasets/
│   └── bug_to_user_story.jsonl   # 15 bug examples
├── src/
│   ├── pull_prompts.py       # Pull from LangSmith
│   ├── push_prompts.py       # Push to LangSmith
│   ├── evaluate.py           # Automatic evaluation
│   ├── metrics.py            # 5 implemented metrics
│   └── utils.py              # Helper functions
└── tests/
    └── test_prompts.py       # Validation tests
```
