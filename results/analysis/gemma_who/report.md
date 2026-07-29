# MIRAGE Pairwise Analysis: gemma_who

## Overall

| Total | Base acc | Tuned acc | Delta | Improved | Worsened | Net |
|---:|---:|---:|---:|---:|---:|---:|
| 7663 | 0.4926 | 0.4762 | -0.0164 | 552 | 678 | -126 |

## By Dataset

| Dataset | Base acc | Tuned acc | Delta | Improved | Worsened | Both correct | Both wrong | Net |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| bioasq | 0.7071 | 0.6683 | -0.0388 | 10 | 34 | 403 | 171 | -24 |
| medmcqa | 0.4466 | 0.4301 | -0.0165 | 345 | 414 | 1454 | 1970 | -69 |
| medqa | 0.4745 | 0.4430 | -0.0314 | 80 | 120 | 484 | 589 | -40 |
| mmlu | 0.5712 | 0.5445 | -0.0266 | 60 | 89 | 533 | 407 | -29 |
| pubmedqa | 0.4880 | 0.5600 | +0.0720 | 57 | 21 | 223 | 199 | 36 |

## Examples

### bioasq

#### improved

- gold=A base=B tuned=A question=Is rilonacept effective for pericarditis?
- gold=B base=A tuned=B question=Do enhancers have to be close to their gene targets?
- gold=A base=B tuned=A question=Do nematodes contain a CTCF gene?
- gold=A base=B tuned=A question=Is the apilimod inhibitor effective against SARS-CoV-2?
- gold=A base=B tuned=A question=Is there an upper limit on the functional fraction of the human genome?

#### worsened

- gold=B base=B tuned=A question=Is levosimendan effective for amyotrophic lateral sclerosis?
- gold=B base=B tuned=A question=Is trichotillomania encountered with equali frequency in males and females?
- gold=B base=B tuned=A question=Is prosopagnosia also known as lack of auditory recognition?
- gold=B base=B tuned=A question=Are Luminopsins a fusion proteins of luminol and Rhodopsin ?
- gold=B base=B tuned=A question=Is Wilson's disease described as an iron storage disease?

#### both_correct

- gold=A base=A tuned=A question=Is PRP-40 regulation of microexons a conserved phenomenon?
- gold=A base=A tuned=A question=Is casimersen effective for the treatment of Duchenne muscular dystrophy?
- gold=B base=B tuned=B question=Is medical hydrology the same as Spa therapy?
- gold=A base=A tuned=A question=Is eteplirsen effective for the treatment of Duchenne muscular dystrophy?
- gold=A base=A tuned=A question=Does CIDEB mutation protect from liver disease?

#### both_wrong

- gold=B base=A tuned=A question=Can losartan reduce brain atrophy in Alzheimer's disease?
- gold=B base=A tuned=A question=Is deflazacort more efficient than prednisone/prednisolone for the treatment of Duchenne muscular dystrophy?
- gold=B base=A tuned=A question=Based on clinical trial data, can pioglitazone delay cognitive impairment for people at risk for Alzheimer's disease?
- gold=B base=A tuned=A question=Does silencing of SRRM4 promote microexon inclusion?
- gold=B base=A tuned=A question=Was erythropoietin effective for optic neuritis in the TONE trial?

### medmcqa

#### improved

- gold=A base=B tuned=A question=Low insulin to glucagon ratio is seen in all of these except:
- gold=A base=D tuned=A question=Heavy forces on periodontal ligament causes:
- gold=A base=C tuned=A question=A patient who was on ventilator and being ventilated for past few days, suddenly pulls out the endotracheal tube. What is the next step of management?
- gold=A base=C tuned=A question=A mother is Hbs Ag positive and anti Hbe Ag positive. Risk of transmission of Hep. B in child is:
- gold=A base=D tuned=A question=The current bar clasp design used is:

#### worsened

- gold=B base=B tuned=A question=A blue new born presents with cyanosis. The X–ray chest reveal oligaemic lung field and normal sized heart. Most likely diagnosis is –
- gold=A base=A tuned=B question=Characteristic of venous blood flow of lower limb in duplex Doppler is?
- gold=B base=B tuned=C question=A pediatrician in a district hospital with specialization neonatal care unit calls an ophthalmologist for consultation for which of the following?
- gold=C base=C tuned=A question=Base pairs in DNA
- gold=C base=C tuned=B question=Calcium ions triggers muscle contraction by binding to:

#### both_correct

- gold=A base=A tuned=A question=Which of the following is not true for myelinated nerve fibers:
- gold=C base=C tuned=C question=A 29 yrs old woman with a pregnancy of 17 week has a 10 years old boy with down syndrome. She does not want another down syndrome kid; best advice to her is
- gold=A base=A tuned=A question=Concentration of tropicamide:
- gold=B base=B tuned=B question=27.	The lateral spread of dental caries is facilitated mostly  by the
- gold=B base=B tuned=B question=Respiratory rhythm generation center is located at:

#### both_wrong

- gold=A base=B tuned=B question=Which of the following is not true about glomerular capillaries')
- gold=C base=A tuned=A question=Axonal transport is:
- gold=A base=C tuned=C question=Which of the following statements is true regarding H I N1 Influenza?
- gold=B base=C tuned=A question=Which of the following are not a branch of external carotid Aery in Kiesselbach's plexus.
- gold=B base=A tuned=A question=Diagnosis of the following ECG-

### medqa

#### improved

- gold=C base=D tuned=C question=A 65-year-old man is brought to the emergency department 30 minutes after the onset of acute chest pain. He has hypertension and asthma. Current medications include atorvastatin, lisinopril, and an albuterol inhaler. He appears pale and diaphoretic. His pulse is 114/min and blood pressure is 130/88 mm Hg. An ECG shows ST-segment depressions in leads II, III, and aVF. Laboratory studies show an increased serum troponin T concentration. The patient is treated for acute coronary syndrome and undergoes percutaneous transluminal coronary angioplasty. At the time of discharge, echocardiography shows a left ventricular ejection fraction of 58%. In addition to aspirin, which of the following drugs should be added to this patient's medication regimen?
- gold=D base=B tuned=D question=A 4-year-old previously healthy boy presents with 4 days of intermittent vomiting and 5-6 daily loose stools. His mother noted bloody stools and decreased oral intake of food and water over the last 24 hours. He is normally in daycare; however, he has been home for the past 3 days. On physical exam his temperature is 102.2°F (39°C), blood pressure is 140/90 mmHg, pulse is 120/min, respirations are 22/min and O2 saturation is 99% on room air. He has dry mucous membranes. On abdominal exam you note diffuse tenderness to palpation without rebound or guarding. There are no masses, hepatosplenomegaly, and bowel sounds are hyperactive. Ultrasound of the right lower quadrant is negative for appendicitis. Stool is guaiac positive. He receives 15mg/kg acetaminophen and fluids are started. The next day, he complains of lower extremity weakness and tingling. On repeat exam, lower extremity strength is 3/5 with diminished patellar deep tendon reflexes. Which of the following lab findings would most likely be seen in this patient?
- gold=D base=C tuned=D question=A 22-year-old woman is brought to the emergency department because of a 2-day history of fever, intermittent rigors, and night sweats. She also has a 1-month history of progressive fatigue. Five weeks ago, she was hospitalized and received intravenous antibiotics for treatment of bacterial meningitis while visiting relatives in Guatemala. Her temperature is 39.4°C (102.9°F), pulse is 130/min, and blood pressure is 105/70 mm Hg. Examination shows pallor and scattered petechiae and ecchymoses. Laboratory studies show a hemoglobin concentration of 9.0 g/dL, a leukocyte count of 1,100/mm3 with 30% segmented neutrophils, and a platelet count of 20,000/mm3 . Blood cultures grow coagulase-negative staphylococci. The patient was most likely treated with which of the following antibiotics?
- gold=D base=C tuned=D question=A 53-year-old man with recurrent pancreatic adenocarcinoma is enrolled in a clinical trial for a novel chemotherapeutic agent that his physician believes may be beneficial to his condition. The novel drug was previously tested in a small population and is now undergoing a larger phase 3 trial in preparation for FDA approval. A dose-response trial had the following results:

10 mg dose - 6/59 patients demonstrated improvement
20 mg dose - 19/49 patients demonstrated improvement
30 mg dose - 26/53 patients demonstrated improvement
40 mg dose - 46/51 patients demonstrated improvement

The same trial also had the following safety profile:

20 mg dose - 5/49 patients had a treatment related adverse event
40 mg dose - 11/51 patients had a treatment related adverse event
60 mg dose - 15/42 patients had a treatment related adverse event
80 mg dose - 23/47 patients had a treatment related adverse event
100 mg dose - 47/52 patients had a treatment related adverse event

Based on this study, which of the following represents the most likely therapeutic index for this novel chemotherapeutic agent?
- gold=A base=C tuned=A question=A 45-year-old G5P4105 presents to her gynecologist’s office with six months of increasingly heavy periods. She now soaks one super absorbent tampon every two hours for five days each cycle. Her cycles have also become irregular, with intermenstrual bleeding for the last two months. She now experiences significant dysmenorrhea, requiring 400 mg ibuprofen every four hours for the majority of each menses. In addition, she reports new onset mild dyspareunia with intercourse and a “heavy feeling” in her pelvis. She has also noticed increased urinary frequency but denies bowel changes. The patient has a past medical history of obesity and type II diabetes on metformin. Her last child was born four years ago, and she has had five spontaneous vaginal deliveries. At this office visit, temperature is 98.5°F (36.9°C), blood pressure is 137/84 mmHg, pulse is 87/min, and respirations are 14/min. Which of the following physical exam findings is most likely to be present in this patient?

#### worsened

- gold=C base=C tuned=B question=A 30-year-old African American woman comes to the physician for the evaluation of a dry cough and chest discomfort for the past 3 days. During this period, the patient has had headaches, muscle aches, joint pain, fever, and chills. Ten days ago, she was hiking with her family in Mississippi. The patient has asthma that is treated with an albuterol inhaler. Her mother has a lung disease treated with methotrexate. The patient has smoked one pack of cigarettes daily for the past 10 years. Her temperature is 38°C (100.4°F). Physical examination shows slight wheezes throughout both lung fields. Laboratory studies and urinalysis are positive for polysaccharide antigen. Bronchoalveolar lavage using silver/PAS-staining shows macrophages filled with a dimorphic fungus with septate hyphae. Which of the following is the most likely cause of this patient's symptoms?
- gold=A base=A tuned=C question=A 67-year-old male is seen by neurology after he was noticed to be speaking strangely by his family. After acute treatment with tissue plasminogen activator (tPA), the patient is able to recover most of his speech. Subsequent neurologic exam finds that the patient is fluent while speaking and is able to comprehend both one and two step instructions. Noticeably the patient remains unable to complete tasks involving verbal repetition. Residual damage to which of the following structures is most likely responsible for this patient's syndrome?
- gold=A base=A tuned=D question=A 55-year-old man comes to the physician because of a 6-week history of tingling pain in the sole of his right foot when he raises it above chest level during exercises. He reports that he started exercising regularly 2 months ago and that his right calf cramps when he uses the incline feature on the treadmill, forcing him to take frequent breaks. The pain completely disappears after resting for a few minutes. He has an 8-year history of type 2 diabetes mellitus. He has smoked two packs of cigarettes daily for 34 years. His only medication is metformin. His pulse is 82/min, and blood pressure is 170/92 mm Hg. Straight leg raise test elicits pallor and tingling pain in the right foot. There is no pain in the back. His muscle strength is normal. Femoral pulses are palpable; right pedal pulses are absent. Which of the following is the most likely diagnosis?
- gold=B base=B tuned=D question=A 29-year-old primigravid woman at 35 weeks' gestation is admitted to the hospital in labor. She has no history of serious medical illness. She has had an uncomplicated pregnancy. Her last ultrasound at 22 weeks' gestation was normal. On admission, fetal heartbeats cannot be detected by fetal doppler monitor. Ultrasound shows decreased amniotic fluid levels and no evidence of fetal movement, respiration, or heart activity. The patient gives birth to a 2296 g (5 lb 1 oz) male infant. Physical examination shows no signs of life. There are no visible malformations. The placenta is unremarkable. Which of the following is the most appropriate next step in management?
- gold=A base=A tuned=C question=A healthy 19-year-old man presents to his primary care provider complaining of painless “blisters” in his mouth. He reports that he noticed a white film on his tongue and the sides of his mouth 2 days ago while brushing his teeth. The film was easily brushed off. He also complains of a bitter metallic taste in his mouth but otherwise denies pain, burning, dysphagia, or hoarseness. He is otherwise healthy and takes no medications. He is a competitive swimmer and has had 8 sexual partners in the past year. He intermittently uses barrier protection. On exam, he is well-appearing and in no acute distress. His oral examination demonstrates patches of white pseudomembranes that can be wiped away to reveal erythematous mucosa. A medication with which of the following mechanisms of action is most appropriate in this patient?

#### both_correct

- gold=D base=D tuned=D question=A 67-year-old man with transitional cell carcinoma of the bladder comes to the physician because of a 2-day history of ringing sensation in his ear. He received this first course of neoadjuvant chemotherapy 1 week ago. Pure tone audiometry shows a sensorineural hearing loss of 45 dB. The expected beneficial effect of the drug that caused this patient's symptoms is most likely due to which of the following actions?
- gold=B base=B tuned=B question=A 35-year-old man comes to the physician because of itchy, watery eyes for the past week. He has also been sneezing multiple times a day during this period. He had a similar episode 1 year ago around springtime. He has iron deficiency anemia and ankylosing spondylitis. Current medications include ferrous sulfate, artificial tear drops, and indomethacin. He works as an elementary school teacher. His vital signs are within normal limits. Visual acuity is 20/20 without correction. Physical examination shows bilateral conjunctival injection with watery discharge. The pupils are 3 mm, equal, and reactive to light. Examination of the anterior chamber of the eye is unremarkable. Which of the following is the most appropriate treatment?
- gold=A base=A tuned=A question=A 23-year-old woman comes to the physician because she is embarrassed about the appearance of her nails. She has no history of serious illness and takes no medications. She appears well. A photograph of the nails is shown. Which of the following additional findings is most likely in this patient?
- gold=D base=D tuned=D question=A 72-year-old man comes to the physician because of a 2-month history of fatigue and worsening abdominal pain. During this period, he also has excessive night sweats and shortness of breath on exertion. Over the past 3 months, he has had a 5.6-kg (12-lb) weight loss. He had a myocardial infarction 3 years ago. He has hypertension, diabetes mellitus, and chronic bronchitis. His medications include insulin, aspirin, lisinopril, and an albuterol inhaler. He has smoked half a pack of cigarettes for the past 45 years. Vital signs are within normal limits. The spleen is palpated 6 cm below the left costal margin. Laboratory studies show:
Hemoglobin 6.4 g/dL
Mean corpuscular volume 85 μm3
Leukocyte count 5,200/mm3
Platelet count 96,000/mm3
A blood smear is shown. Bone marrow aspiration shows extensive fibrosis and a few scattered plasma cells. A JAK 2 assay is positive. Which of the following is the most appropriate next step in management?"
- gold=B base=B tuned=B question=A 59-year-old overweight woman presents to the urgent care clinic with the complaint of severe abdominal pain for the past 2 hours. She also complains of a dull pain in her back with nausea and vomiting several times. Her pain has no relation with food. Her past medical history is significant for recurrent abdominal pain due to cholelithiasis. Her father died at the age of 60 with some form of abdominal cancer. Her temperature is 37°C (98.6°F), respirations are 15/min, pulse is 67/min, and blood pressure is 122/98 mm Hg. Physical exam is unremarkable. However, a CT scan of the abdomen shows a calcified mass near her gallbladder. Which of the following diagnoses should be excluded first in this patient?

#### both_wrong

- gold=B base=A tuned=A question=A junior orthopaedic surgery resident is completing a carpal tunnel repair with the department chairman as the attending physician. During the case, the resident inadvertently cuts a flexor tendon. The tendon is repaired without complication. The attending tells the resident that the patient will do fine, and there is no need to report this minor complication that will not harm the patient, as he does not want to make the patient worry unnecessarily. He tells the resident to leave this complication out of the operative report. Which of the following is the correct next action for the resident to take?
- gold=B base=C tuned=A question=Two weeks after undergoing an emergency cardiac catherization with stenting for unstable angina pectoris, a 61-year-old man has decreased urinary output and malaise. He has type 2 diabetes mellitus and osteoarthritis of the hips. Prior to admission, his medications were insulin and naproxen. He was also started on aspirin, clopidogrel, and metoprolol after the coronary intervention. His temperature is 38°C (100.4°F), pulse is 93/min, and blood pressure is 125/85 mm Hg. Examination shows mottled, reticulated purplish discoloration of the feet. Laboratory studies show:
Hemoglobin count 14 g/dL
Leukocyte count 16,400/mm3
Segmented neutrophils 56%
Eosinophils 11%
Lymphocytes 31%
Monocytes 2%
Platelet count 260,000/mm3
Erythrocyte sedimentation rate 68 mm/h
Serum
Urea nitrogen 25 mg/dL
Creatinine 4.2 mg/dL
Renal biopsy shows intravascular spindle-shaped vacuoles. Which of the following is the most likely cause of this patient's symptoms?"
- gold=D base=A tuned=A question=A 39-year-old woman is brought to the emergency department because of fevers, chills, and left lower quadrant pain. Her temperature is 39.1°C (102.3°F), pulse is 126/min, respirations are 28/min, and blood pressure is 80/50 mm Hg. There is blood oozing around the site of a peripheral intravenous line. Pelvic examination shows mucopurulent discharge from the cervical os and left adnexal tenderness. Laboratory studies show:
Platelet count 14,200/mm3
Fibrinogen 83 mg/mL (N = 200–430 mg/dL)
D-dimer 965 ng/mL (N < 500 ng/mL)
When phenol is applied to a sample of the patient's blood at 90°C, a phosphorylated N-acetylglucosamine dimer with 6 fatty acids attached to a polysaccharide side chain is identified. A blood culture is most likely to show which of the following?"
- gold=D base=B tuned=A question=A 39-year-old man presents to the emergency department because of progressively worsening chest pain and nausea that started at a local bar 30 minutes prior. The pain radiates to the epigastric area. He has a 5-year history of untreated hypertension. He has smoked 1 pack of cigarettes daily for the past 5 years and started abusing cocaine 2 weeks before his emergency room visit. The patient is diaphoretic and in marked distress. What should be the first step in management?
- gold=C base=D tuned=D question=A 68-year-old male comes to the physician for evaluation of right flank pain. He has a history of diabetes and peripheral artery disease. His blood pressure is 160/90 mm Hg. Physical examination shows abdominal tenderness and right flank tenderness. An ultrasound shows dilation of the right ureter and renal pelvis. Which of the following is the most likely underlying cause of this patient's condition?

### mmlu

#### improved

- gold=B base=D tuned=B question=Which muscles are normally active during quiet inspiration?
- gold=D base=A tuned=D question=Oxygenated blood is carried to the heart by which of the following structures?
- gold=A base=D tuned=A question=The mucosa of the upper larynx is innervated by the
- gold=A base=D tuned=A question=The infraorbital nerve
- gold=D base=A tuned=D question=Which one of the following brain areas is supplied by branches of the subclavian arteries?

#### worsened

- gold=B base=B tuned=A question=A "dished face" profile is often associated with
- gold=B base=B tuned=C question=Laryngoscopic examination of the vocal folds after suspected recurrent laryngeal nerve damage usually shows that the vocal fold on the injured side is tensed and in an intermediate position between adduction and abduction. This is because
- gold=A base=A tuned=D question=The coronal suture joins the
- gold=B base=B tuned=A question=The anatomic location of the spinal canal is
- gold=C base=C tuned=A question=The head of the sixth rib articulates with

#### both_correct

- gold=A base=A tuned=A question=Which of the following best describes the structure that collects urine in the body?
- gold=C base=C tuned=C question=Which of the following structures is derived from ectomesenchyme?
- gold=B base=B tuned=B question=Which of the following describes the cluster of blood capillaries found in each nephron in the kidney?
- gold=A base=A tuned=A question=Which of the following anatomical regions of abdomen lies just distal to the sternum?
- gold=B base=B tuned=B question=Which of the following best describes the human body's defense mechanism against environmental bacteria?

#### both_wrong

- gold=A base=C tuned=C question=A lesion causing compression of the facial nerve at the stylomastoid foramen will cause ipsilateral
- gold=B base=A tuned=A question=A patient suffers a broken neck with damage to the spinal cord at the level of the sixth cervical vertebra.
- gold=C base=B tuned=B question=The palatine processes begin to fuse at
- gold=D base=B tuned=A question=Primary motor cortex activity results in
- gold=D base=C tuned=C question=You notice that your patient's submandibular lymph nodes are enlarged. You would look for potential infection sites in the

### pubmedqa

#### improved

- gold=A base=C tuned=A question="Occult" posttraumatic lesions of the knee: can magnetic resonance substitute for diagnostic arthroscopy?
- gold=A base=B tuned=A question=Is portable ultrasonography accurate in the evaluation of Schanz pin placement during extremity fracture fixation in austere environments?
- gold=A base=C tuned=A question=Proof of concept study: does fenofibrate have a role in sleep apnoea syndrome?
- gold=A base=C tuned=A question=Differentiation of nonalcoholic from alcoholic steatohepatitis: are routine laboratory markers useful?
- gold=A base=C tuned=A question=The Prevalence of Incidentally Detected Idiopathic Misty Mesentery on Multidetector Computed Tomography: Can Obesity Be the Triggering Cause?

#### worsened

- gold=B base=B tuned=A question=Department of Transportation vs self-reported data on motor vehicle collisions and driving convictions for stroke survivors: do they agree?
- gold=B base=B tuned=A question=Do African American women require fewer calories to maintain weight?
- gold=B base=B tuned=A question=The use of audit to identify maternal mortality in different settings: is it just a difference between the rich and the poor?
- gold=B base=B tuned=A question=Are the long-term results of the transanal pull-through equal to those of the transabdominal pull-through?
- gold=B base=B tuned=A question=Do foreign bodies migrate through the body towards the heart?

#### both_correct

- gold=A base=A tuned=A question=Is anorectal endosonography valuable in dyschesia?
- gold=A base=A tuned=A question=Is there a connection between sublingual varices and hypertension?
- gold=A base=A tuned=A question=Is the affinity column-mediated immunoassay method suitable as an alternative to the microparticle enzyme immunoassay method as a blood tacrolimus assay?
- gold=A base=A tuned=A question=Does a physician's specialty influence the recording of medication history in patients' case notes?
- gold=A base=A tuned=A question=Locoregional opening of the rodent blood-brain barrier for paclitaxel using Nd:YAG laser-induced thermo therapy: a new concept of adjuvant glioma therapy?

#### both_wrong

- gold=A base=B tuned=B question=Do patients with rheumatoid arthritis established on methotrexate and folic acid 5 mg daily need to continue folic acid supplements long term?
- gold=A base=B tuned=B question=Assessing Patient Reported Outcomes Measures via Phone Interviews Versus Patient Self-Survey in the Clinic: Are We Measuring the Same Thing?
- gold=A base=C tuned=B question=Is it appropriate to implant kidneys from elderly donors in young recipients?
- gold=A base=B tuned=B question=Implementation of epidural analgesia for labor: is the standard of effective analgesia reachable in all women?
- gold=A base=B tuned=B question=Longer term quality of life and outcome in stroke patients: is the Barthel index alone an adequate measure of outcome?

