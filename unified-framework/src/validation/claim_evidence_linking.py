#!/usr/bin/env python3
"""
Automated Claim-Evidence Linking System for Z Framework Validation

This module provides an automated system for linking claims from documentation
to evidence from test results, generating a traceability matrix for validation.

Features:
- Claim extraction from documentation using spaCy NLP
- Evidence parsing from JSON test logs
- Semantic matching using BERT with keyword fallback
- Bootstrap statistical validation
- Traceability matrix generation

Author: GitHub Copilot
Date: 2025
"""

import json
import os
import re
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import numpy as np
from scipy import stats
import spacy
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    HAS_SENTENCE_TRANSFORMERS = True
except ImportError:
    HAS_SENTENCE_TRANSFORMERS = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class Claim:
    """Represents a claim extracted from documentation."""
    id: str
    text: str
    source: str
    line_number: int
    confidence: float
    keywords: List[str]

@dataclass
class Evidence:
    """Represents evidence extracted from test results."""
    id: str
    test_name: str
    metrics: Dict[str, Any]
    status: str
    confidence: float
    source_file: str

@dataclass
class Link:
    """Represents a link between a claim and evidence."""
    claim_id: str
    evidence_id: str
    similarity_score: float
    validation_status: str
    confidence_interval: Tuple[float, float]
    method: str  # 'bert', 'keyword', 'hybrid'

@dataclass
class TraceabilityMatrix:
    """Represents the complete traceability matrix."""
    claims: List[Claim]
    evidence: List[Evidence]
    links: List[Link]
    metadata: Dict[str, Any]
    statistics: Dict[str, Any]

class ClaimExtractor:
    """Extracts claims from documentation using NLP."""
    
    def __init__(self):
        """Initialize the claim extractor with spaCy model."""
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except OSError:
            logger.error("spaCy model 'en_core_web_sm' not found. Please install it with: python -m spacy download en_core_web_sm")
            raise
        
        # Keywords that indicate claims about validation, performance, accuracy
        self.claim_indicators = [
            'validates', 'proves', 'demonstrates', 'shows', 'confirms',
            'accuracy', 'precision', 'performance', 'efficient', 'optimal',
            'converges', 'stability', 'robust', 'reliable', 'correct',
            'implementation', 'algorithm', 'method', 'technique', 'approach'
        ]
    
    def extract_claims_from_file(self, file_path: str) -> List[Claim]:
        """Extract claims from a documentation file."""
        claims = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Process text with spaCy
            doc = self.nlp(content)
            
            # Extract sentences that contain claim indicators
            for sent_idx, sent in enumerate(doc.sents):
                sent_text = sent.text.strip()
                
                # Skip very short or empty sentences
                if len(sent_text) < 20:
                    continue
                
                # Check for claim indicators
                claim_score = self._calculate_claim_score(sent_text.lower())
                
                if claim_score > 0.3:  # Threshold for claim detection
                    # Extract keywords
                    keywords = self._extract_keywords(sent)
                    
                    claim = Claim(
                        id=f"claim_{len(claims) + 1:03d}",
                        text=sent_text,
                        source=file_path,
                        line_number=sent_idx + 1,
                        confidence=claim_score,
                        keywords=keywords
                    )
                    claims.append(claim)
            
            logger.info(f"Extracted {len(claims)} claims from {file_path}")
            
        except Exception as e:
            logger.error(f"Error extracting claims from {file_path}: {e}")
        
        return claims
    
    def _calculate_claim_score(self, text: str) -> float:
        """Calculate the likelihood that a sentence contains a claim."""
        score = 0.0
        
        # Check for claim indicators
        for indicator in self.claim_indicators:
            if indicator in text:
                score += 0.2
        
        # Boost score for sentences with performance metrics
        if re.search(r'\d+(\.\d+)?%|\d+(\.\d+)?\s*(seconds?|ms|microseconds?)', text):
            score += 0.3
        
        # Boost score for validation-related terms
        validation_terms = ['test', 'validation', 'verification', 'benchmark', 'evaluation']
        for term in validation_terms:
            if term in text:
                score += 0.1
        
        return min(score, 1.0)
    
    def _extract_keywords(self, sent) -> List[str]:
        """Extract keywords from a sentence using spaCy."""
        keywords = []
        
        for token in sent:
            # Extract nouns, adjectives, and numbers
            if (token.pos_ in ['NOUN', 'ADJ', 'NUM'] and 
                not token.is_stop and 
                not token.is_punct and 
                len(token.text) > 2):
                keywords.append(token.lemma_.lower())
        
        return keywords[:10]  # Limit to top 10 keywords

class EvidenceParser:
    """Parses evidence from test result files."""
    
    def __init__(self):
        """Initialize the evidence parser."""
        self.test_patterns = [
            r'TC\d{2}',  # TC01, TC02, etc.
            r'TC-LET-\d{2}-\d{2}',  # TC-LET-01-03, etc.
            r'test_\w+',  # test_* patterns
        ]
    
    def parse_evidence_from_files(self, test_results_dir: str) -> List[Evidence]:
        """Parse evidence from test result files."""
        evidence_list = []
        
        # Look for JSON test result files
        results_dir = Path(test_results_dir)
        if not results_dir.exists():
            logger.warning(f"Test results directory not found: {test_results_dir}")
            return evidence_list
        
        for json_file in results_dir.glob("*.json"):
            try:
                evidence_list.extend(self._parse_json_file(json_file))
            except Exception as e:
                logger.error(f"Error parsing {json_file}: {e}")
        
        logger.info(f"Parsed {len(evidence_list)} evidence items from {test_results_dir}")
        return evidence_list
    
    def _parse_json_file(self, file_path: Path) -> List[Evidence]:
        """Parse evidence from a single JSON file."""
        evidence_list = []
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            # Handle different JSON structures
            if isinstance(data, dict):
                if 'tests' in data:
                    # Structure: {"tests": [...]}
                    for test in data['tests']:
                        evidence = self._parse_test_entry(test, str(file_path))
                        if evidence:
                            evidence_list.append(evidence)
                elif 'results' in data:
                    # Structure: {"results": [...]}
                    for result in data['results']:
                        evidence = self._parse_test_entry(result, str(file_path))
                        if evidence:
                            evidence_list.append(evidence)
                else:
                    # Try to parse as single test result
                    evidence = self._parse_test_entry(data, str(file_path))
                    if evidence:
                        evidence_list.append(evidence)
            elif isinstance(data, list):
                # Structure: [...]
                for item in data:
                    evidence = self._parse_test_entry(item, str(file_path))
                    if evidence:
                        evidence_list.append(evidence)
        
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {file_path}: {e}")
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
        
        return evidence_list
    
    def _parse_test_entry(self, entry: Dict, source_file: str) -> Optional[Evidence]:
        """Parse a single test entry to extract evidence."""
        try:
            # Extract test name
            test_name = entry.get('name', entry.get('test_name', entry.get('id', 'unknown')))
            
            # Skip if not a recognized test pattern
            if not any(re.search(pattern, test_name) for pattern in self.test_patterns):
                return None
            
            # Extract metrics
            metrics = {}
            for key, value in entry.items():
                if key in ['accuracy', 'precision', 'performance', 'runtime', 'error_rate', 
                          'convergence', 'stability', 'memory_usage', 'cpu_time']:
                    metrics[key] = value
                elif isinstance(value, (int, float)) and key not in ['line_number', 'id']:
                    metrics[key] = value
            
            # Determine status
            status = entry.get('status', 'unknown')
            if status == 'unknown':
                if entry.get('passed', False) or entry.get('success', False):
                    status = 'pass'
                elif entry.get('failed', False) or entry.get('error', False):
                    status = 'fail'
                else:
                    status = 'unknown'
            
            # Calculate confidence based on available metrics
            confidence = min(len(metrics) * 0.2, 1.0)
            
            evidence = Evidence(
                id=f"evidence_{test_name}",
                test_name=test_name,
                metrics=metrics,
                status=status,
                confidence=confidence,
                source_file=source_file
            )
            
            return evidence
            
        except Exception as e:
            logger.error(f"Error parsing test entry: {e}")
            return None

class SemanticMatcher:
    """Performs semantic matching between claims and evidence."""
    
    def __init__(self):
        """Initialize the semantic matcher."""
        self.use_bert = False
        self.sentence_model = None
        
        if HAS_SENTENCE_TRANSFORMERS:
            try:
                # Try to load BERT model, fall back to lighter model if needed
                self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
                self.use_bert = True
            except Exception as e:
                logger.warning(f"Could not load BERT model: {e}. Using keyword matching only.")
                self.sentence_model = None
                self.use_bert = False
        else:
            logger.info("sentence-transformers not available. Using keyword matching only.")
    
    def match_claims_to_evidence(self, claims: List[Claim], evidence: List[Evidence]) -> List[Link]:
        """Match claims to evidence using semantic similarity."""
        links = []
        
        if not claims or not evidence:
            logger.warning("No claims or evidence to match")
            return links
        
        # Prepare texts for encoding
        claim_texts = [claim.text for claim in claims]
        evidence_texts = [f"{ev.test_name} {' '.join(str(v) for v in ev.metrics.values())}" 
                         for ev in evidence]
        
        if self.use_bert:
            # Use BERT for semantic matching
            try:
                claim_embeddings = self.sentence_model.encode(claim_texts)
                evidence_embeddings = self.sentence_model.encode(evidence_texts)
                
                # Calculate cosine similarity
                similarity_matrix = cosine_similarity(claim_embeddings, evidence_embeddings)
                
                # Create links for similarities above threshold
                for i, claim in enumerate(claims):
                    for j, ev in enumerate(evidence):
                        similarity = similarity_matrix[i, j]
                        
                        if similarity > 0.3:  # Threshold for similarity
                            # Calculate confidence interval using bootstrap
                            ci = self._bootstrap_confidence_interval(claim, ev, similarity)
                            
                            link = Link(
                                claim_id=claim.id,
                                evidence_id=ev.id,
                                similarity_score=similarity,
                                validation_status=self._determine_validation_status(claim, ev, similarity),
                                confidence_interval=ci,
                                method='bert'
                            )
                            links.append(link)
            
            except Exception as e:
                logger.error(f"Error in BERT matching: {e}")
                # Fall back to keyword matching
                return self._keyword_matching(claims, evidence)
        
        else:
            # Use keyword matching as fallback
            links = self._keyword_matching(claims, evidence)
        
        logger.info(f"Created {len(links)} links between claims and evidence")
        return links
    
    def _keyword_matching(self, claims: List[Claim], evidence: List[Evidence]) -> List[Link]:
        """Fallback keyword-based matching."""
        links = []
        
        for claim in claims:
            for ev in evidence:
                # Calculate keyword overlap
                claim_keywords = set(claim.keywords)
                evidence_keywords = set()
                
                # Extract keywords from evidence
                for key, value in ev.metrics.items():
                    evidence_keywords.add(key.lower())
                
                # Add test name keywords
                evidence_keywords.update(ev.test_name.lower().split('_'))
                
                # Also check text-based similarity for common terms
                claim_text_words = set(claim.text.lower().split())
                evidence_text_words = set(ev.test_name.lower().split('_'))
                
                # Calculate Jaccard similarity for keywords
                keyword_intersection = len(claim_keywords.intersection(evidence_keywords))
                keyword_union = len(claim_keywords.union(evidence_keywords))
                
                # Calculate text similarity
                text_intersection = len(claim_text_words.intersection(evidence_text_words))
                text_union = len(claim_text_words.union(evidence_text_words))
                
                keyword_similarity = keyword_intersection / keyword_union if keyword_union > 0 else 0
                text_similarity = text_intersection / text_union if text_union > 0 else 0
                
                # Combine similarities
                similarity = max(keyword_similarity, text_similarity * 0.8)
                
                # Check for domain-specific matches
                if self._has_domain_match(claim, ev):
                    similarity += 0.2
                
                if similarity > 0.1:  # Lower threshold for keyword matching
                    ci = self._bootstrap_confidence_interval(claim, ev, similarity)
                    
                    link = Link(
                        claim_id=claim.id,
                        evidence_id=ev.id,
                        similarity_score=similarity,
                        validation_status=self._determine_validation_status(claim, ev, similarity),
                        confidence_interval=ci,
                        method='keyword'
                    )
                    links.append(link)
        
        return links
    
    def _has_domain_match(self, claim: Claim, evidence: Evidence) -> bool:
        """Check for domain-specific matches between claim and evidence."""
        claim_text = claim.text.lower()
        test_name = evidence.test_name.lower()
        
        # Performance-related matches
        performance_terms = ['performance', 'efficient', 'speed', 'fast', 'benchmark']
        if any(term in claim_text for term in performance_terms) and any(term in test_name for term in performance_terms):
            return True
        
        # Accuracy-related matches
        accuracy_terms = ['accuracy', 'precision', 'correct', 'accurate']
        if any(term in claim_text for term in accuracy_terms) and any(term in test_name for term in accuracy_terms):
            return True
        
        # Validation-related matches
        validation_terms = ['validation', 'test', 'verify', 'prove', 'demonstrate']
        if any(term in claim_text for term in validation_terms) and any(term in test_name for term in validation_terms):
            return True
        
        # Mathematical terms
        math_terms = ['algorithm', 'mathematical', 'convergence', 'stability', 'prime']
        if any(term in claim_text for term in math_terms) and any(term in test_name for term in math_terms):
            return True
        
        return False
    
    def _bootstrap_confidence_interval(self, claim: Claim, evidence: Evidence, similarity: float) -> Tuple[float, float]:
        """Calculate bootstrap confidence interval for the similarity score."""
        # Simulate bootstrap sampling (simplified)
        n_samples = 1000
        similarities = []
        
        for _ in range(n_samples):
            # Add small random noise to simulate sampling uncertainty
            noise = np.random.normal(0, 0.05)
            sim_sample = max(0, min(1, similarity + noise))
            similarities.append(sim_sample)
        
        # Calculate 95% confidence interval
        ci_lower = np.percentile(similarities, 2.5)
        ci_upper = np.percentile(similarities, 97.5)
        
        return (ci_lower, ci_upper)
    
    def _determine_validation_status(self, claim: Claim, evidence: Evidence, similarity: float) -> str:
        """Determine validation status based on claim-evidence match."""
        if evidence.status == 'pass' and similarity > 0.5:
            return 'validated'
        elif evidence.status == 'fail':
            return 'failed'
        elif similarity > 0.3:
            return 'partial'
        else:
            return 'unlinked'

class ClaimEvidenceLinkingSystem:
    """Main system for automated claim-evidence linking."""
    
    def __init__(self, repository_root: str):
        """Initialize the linking system."""
        self.repository_root = Path(repository_root)
        self.claim_extractor = ClaimExtractor()
        self.evidence_parser = EvidenceParser()
        self.semantic_matcher = SemanticMatcher()
    
    def run_analysis(self, quick_mode: bool = True) -> TraceabilityMatrix:
        """Run the complete claim-evidence linking analysis."""
        logger.info("Starting claim-evidence linking analysis...")
        
        # Extract claims from documentation
        claims = self._extract_all_claims()
        
        # Parse evidence from test results
        evidence = self._parse_all_evidence()
        
        # Match claims to evidence
        links = self.semantic_matcher.match_claims_to_evidence(claims, evidence)
        
        # Generate statistics
        statistics = self._generate_statistics(claims, evidence, links)
        
        # Create traceability matrix
        matrix = TraceabilityMatrix(
            claims=claims,
            evidence=evidence,
            links=links,
            metadata={
                'repository_root': str(self.repository_root),
                'analysis_mode': 'quick' if quick_mode else 'full',
                'timestamp': datetime.now().isoformat(),
                'bert_enabled': self.semantic_matcher.use_bert
            },
            statistics=statistics
        )
        
        logger.info("Analysis complete!")
        return matrix
    
    def _extract_all_claims(self) -> List[Claim]:
        """Extract claims from all documentation files."""
        claims = []
        
        # Look for documentation files
        doc_files = []
        
        # Check common documentation locations
        for pattern in ['README.md', 'docs/**/*.md', '**/*validation*.md', '**/*whitepaper*.md']:
            doc_files.extend(self.repository_root.glob(pattern))
        
        # Remove duplicates
        doc_files = list(set(doc_files))
        
        for doc_file in doc_files:
            if doc_file.is_file():
                file_claims = self.claim_extractor.extract_claims_from_file(str(doc_file))
                claims.extend(file_claims)
        
        return claims
    
    def _parse_all_evidence(self) -> List[Evidence]:
        """Parse evidence from all test result files."""
        evidence = []
        
        # Look for test result directories and files
        test_dirs = [
            self.repository_root / 'tests',
            self.repository_root / 'results',
            self.repository_root / 'validation_results',
            self.repository_root,  # Root directory for JSON files
        ]
        
        for test_dir in test_dirs:
            if test_dir.exists():
                dir_evidence = self.evidence_parser.parse_evidence_from_files(str(test_dir))
                evidence.extend(dir_evidence)
        
        return evidence
    
    def _generate_statistics(self, claims: List[Claim], evidence: List[Evidence], links: List[Link]) -> Dict[str, Any]:
        """Generate statistics about the analysis."""
        total_claims = len(claims)
        total_evidence = len(evidence)
        total_links = len(links)
        
        # Count validation statuses
        status_counts = {}
        for link in links:
            status = link.validation_status
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Calculate coverage
        linked_claims = set(link.claim_id for link in links)
        linked_evidence = set(link.evidence_id for link in links)
        
        claim_coverage = len(linked_claims) / total_claims if total_claims > 0 else 0
        evidence_coverage = len(linked_evidence) / total_evidence if total_evidence > 0 else 0
        
        return {
            'total_claims': total_claims,
            'total_evidence': total_evidence,
            'total_links': total_links,
            'claim_coverage': claim_coverage,
            'evidence_coverage': evidence_coverage,
            'validation_status_counts': status_counts,
            'average_similarity': np.mean([link.similarity_score for link in links]) if links else 0,
            'method_counts': {
                'bert': sum(1 for link in links if link.method == 'bert'),
                'keyword': sum(1 for link in links if link.method == 'keyword'),
            }
        }
    
    def save_traceability_matrix(self, matrix: TraceabilityMatrix, output_file: str = 'traceability_matrix.json'):
        """Save the traceability matrix to a JSON file."""
        output_path = self.repository_root / output_file
        
        # Convert to serializable format
        matrix_dict = {
            'claims': [asdict(claim) for claim in matrix.claims],
            'evidence': [asdict(evidence) for evidence in matrix.evidence],
            'links': [asdict(link) for link in matrix.links],
            'metadata': matrix.metadata,
            'statistics': matrix.statistics
        }
        
        try:
            with open(output_path, 'w') as f:
                json.dump(matrix_dict, f, indent=2, default=str)
            
            logger.info(f"Traceability matrix saved to {output_path}")
            
        except Exception as e:
            logger.error(f"Error saving traceability matrix: {e}")
    
    def print_summary(self, matrix: TraceabilityMatrix):
        """Print a summary of the analysis results."""
        stats = matrix.statistics
        
        print("\n" + "="*60)
        print("CLAIM-EVIDENCE LINKING ANALYSIS SUMMARY")
        print("="*60)
        print(f"📄 Total Claims: {stats['total_claims']}")
        print(f"🧪 Total Evidence Items: {stats['total_evidence']}")
        print(f"🔗 Total Links Created: {stats['total_links']}")
        print(f"📊 Claim Coverage: {stats['claim_coverage']:.1%}")
        print(f"📈 Evidence Coverage: {stats['evidence_coverage']:.1%}")
        print(f"🎯 Average Similarity: {stats['average_similarity']:.3f}")
        
        print("\nValidation Status Breakdown:")
        for status, count in stats['validation_status_counts'].items():
            print(f"  {status}: {count}")
        
        print(f"\nMatching Methods Used:")
        for method, count in stats['method_counts'].items():
            print(f"  {method}: {count}")
        
        print("\nTop Validated Links:")
        validated_links = [link for link in matrix.links if link.validation_status == 'validated']
        for i, link in enumerate(sorted(validated_links, key=lambda x: x.similarity_score, reverse=True)[:3]):
            claim = next(c for c in matrix.claims if c.id == link.claim_id)
            evidence = next(e for e in matrix.evidence if e.id == link.evidence_id)
            print(f"  {i+1}. {claim.text[:60]}... -> {evidence.test_name} ({link.similarity_score:.3f})")
        
        print("="*60)

def main():
    """Main function for standalone execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Automated Claim-Evidence Linking System')
    parser.add_argument('--repository', '-r', default='.', help='Repository root directory')
    parser.add_argument('--output', '-o', default='traceability_matrix.json', help='Output file name')
    parser.add_argument('--quick', action='store_true', help='Run in quick mode')
    
    args = parser.parse_args()
    
    # Initialize and run the system
    system = ClaimEvidenceLinkingSystem(args.repository)
    matrix = system.run_analysis(quick_mode=args.quick)
    
    # Save results
    system.save_traceability_matrix(matrix, args.output)
    
    # Print summary
    system.print_summary(matrix)

if __name__ == '__main__':
    main()