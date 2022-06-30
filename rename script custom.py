
try:
	# these imports work if running from GUI
	from . import nuthouse01_core as core
	from . import nuthouse01_pmx_parser as pmxlib
	from . import nuthouse01_pmx_struct as pmxstruct
	from ._prune_unused_bones import insert_single_bone
except ImportError as eee:
	try:
		# these imports work if running from double-click on THIS script
		import nuthouse01_core as core
		import nuthouse01_pmx_parser as pmxlib
		import nuthouse01_pmx_struct as pmxstruct
		from _prune_unused_bones import insert_single_bone
	except ImportError as eee:
		print(eee.__class__.__name__, eee)
		print(
			"ERROR: failed to import some of the necessary files, all my scripts must be together in the same folder!")
		print("...press ENTER to exit...")
		input()
		exit()
		core = pmxlib = pmxstruct = insert_single_bone = None

helptext = '''=================================================
This will translate your Source model bone names to Japanese and add all the necessary bones while at it.
Modified for Ryza 2,Maximo models and Koikatsu
'''

caution_message = '''
This will not 100% make your model work as intended.
'''

instructions = '''
This is not a a full plug-and-play script. You still need to work a little to finalize your model.
After you are done with the script, open `yourfilename_sourcetrans.pmx`, merge similar bone by names through
menu Edit (E), Bone (B), Merge bone with similar name (M).
The model may need to be scaled down somewhat (see 'model_scale.py') and the core/base bones might need to be repositioned.
Since this is not plug-and-play, your model weight and UV won't always work perfectly with the motions, try to
move the bones around, merge unused bones, and change the pose to avoid animation glitches.
'''

known_issues = '''
* Positions of your base bones will varied depends on whether your model is generic or a little bit less generic. 
You should move the base bones like "腰" and "グルーブ" if it is really needed since most of the time they are just there
'''

# This takes PMX output from Crowbar
# New BIP
finger_dict = {
	"右小指１": ["cf_J_Hand_Little01_R", "mixamorig:RightHandPinky1", "ValveBiped.Bip01_R_Finger4", "bip_pinky_0_R", "SK_R_Pinky01"],
	"右小指２": ["cf_J_Hand_Little02_R", "mixamorig:RightHandPinky2", "ValveBiped.Bip01_R_Finger41", "bip_pinky_1_R", "SK_R_Pinky02"],
	"右小指３": ["cf_J_Hand_Little03_R", "mixamorig:RightHandPinky3", "ValveBiped.Bip01_R_Finger42", "bip_pinky_2_R", "SK_R_Pinky03"],
	"右薬指１": ["cf_J_Hand_Ring01_R", "mixamorig:RightHandRing1", "ValveBiped.Bip01_R_Finger3", "bip_ring_0_R", "SK_R_Ring01"],
	"右薬指２": ["cf_J_Hand_Ring02_R", "mixamorig:RightHandRing2", "ValveBiped.Bip01_R_Finger31", "bip_ring_1_R", "SK_R_Ring02"],
	"右薬指３": ["cf_J_Hand_Ring03_R", "mixamorig:RightHandRing3", "ValveBiped.Bip01_R_Finger32", "bip_ring_2_R", "SK_R_Ring03"],
	"右中指１": ["cf_J_Hand_Middle01_R", "mixamorig:RightHandMiddle1", "ValveBiped.Bip01_R_Finger2", "bip_middle_0_R", "SK_R_Middle01"],
	"右中指２": ["cf_J_Hand_Middle02_R", "mixamorig:RightHandMiddle2", "ValveBiped.Bip01_R_Finger21", "bip_middle_1_R", "SK_R_Middle02"],
	"右中指３": ["cf_J_Hand_Middle03_R", "mixamorig:RightHandMiddle3", "ValveBiped.Bip01_R_Finger22", "bip_middle_2_R", "SK_R_Middle03"],
	"右人指１": ["cf_J_Hand_Index01_R", "mixamorig:RightHandIndex1", "ValveBiped.Bip01_R_Finger1", "bip_index_0_R", "SK_R_Index01"],
	"右人指２": ["cf_J_Hand_Index02_R", "mixamorig:RightHandIndex2", "ValveBiped.Bip01_R_Finger11", "bip_index_1_R", "SK_R_Index02"],
	"右人指３": ["cf_J_Hand_Index03_R", "mixamorig:RightHandIndex3", "ValveBiped.Bip01_R_Finger12", "bip_index_2_R", "SK_R_Index03"],
	"右親指０": ["cf_J_Hand_Thumb01_R", "mixamorig:RightHandThumb1", "ValveBiped.Bip01_R_Finger0", "bip_thumb_0_R", "SK_R_Thumb01"],
	"右親指１": ["cf_J_Hand_Thumb02_R", "mixamorig:RightHandThumb2", "ValveBiped.Bip01_R_Finger01", "bip_thumb_1_R", "SK_R_Thumb02"],
	"右親指２": ["cf_J_Hand_Thumb03_R", "mixamorig:RightHandThumb3", "ValveBiped.Bip01_R_Finger02", "bip_thumb_2_R", "SK_R_Thumb03"],  # no bone for the second joint here but anyway
	
	"左小指１": ["cf_J_Hand_Little01_L", "mixamorig:LeftHandPinky1", "ValveBiped.Bip01_L_Finger4", "bip_pinky_0_L", "SK_L_Pinky01"],
	"左小指２": ["cf_J_Hand_Little02_L", "mixamorig:LeftHandPinky2", "ValveBiped.Bip01_L_Finger41", "bip_pinky_1_L", "SK_L_Pinky02"],
	"左小指３": ["cf_J_Hand_Little03_L", "mixamorig:LeftHandPinky3", "ValveBiped.Bip01_L_Finger42", "bip_pinky_2_L", "SK_L_Pinky03"],
	"左薬指１": ["cf_J_Hand_Ring01_L", "mixamorig:LeftHandRing1", "ValveBiped.Bip01_L_Finger3", "bip_ring_0_L", "SK_L_Ring01"],
	"左薬指２": ["cf_J_Hand_Ring02_L", "mixamorig:LeftHandRing2", "ValveBiped.Bip01_L_Finger31", "bip_ring_1_L", "SK_L_Ring02"],
	"左薬指３": ["cf_J_Hand_Ring03_L", "mixamorig:LeftHandRing3", "ValveBiped.Bip01_L_Finger32", "bip_ring_2_L", "SK_L_Ring03"],
	"左中指１": ["cf_J_Hand_Middle01_L", "mixamorig:LeftHandMiddle1", "ValveBiped.Bip01_L_Finger2", "bip_middle_0_L", "SK_L_Middle01"],
	"左中指２": ["cf_J_Hand_Middle02_L", "mixamorig:LeftHandMiddle2", "ValveBiped.Bip01_L_Finger21", "bip_middle_1_L", "SK_L_Middle02"],
	"左中指３": ["cf_J_Hand_Middle03_L", "mixamorig:LeftHandMiddle3", "ValveBiped.Bip01_L_Finger22", "bip_middle_2_L", "SK_L_Middle03"],
	"左人指１": ["cf_J_Hand_Index01_L", "mixamorig:LeftHandIndex1", "ValveBiped.Bip01_L_Finger1", "bip_index_0_L", "SK_L_Index01"],
	"左人指２": ["cf_J_Hand_Index02_L", "mixamorig:LeftHandIndex2", "ValveBiped.Bip01_L_Finger11", "bip_index_1_L", "SK_L_Index02"],
	"左人指３": ["cf_J_Hand_Index03_L", "mixamorig:LeftHandIndex3", "ValveBiped.Bip01_L_Finger12", "bip_index_2_L", "SK_L_Index03"],
	"左親指０": ["cf_J_Hand_Thumb01_L", "mixamorig:LeftHandThumb1", "ValveBiped.Bip01_L_Finger0", "bip_thumb_0_L", "SK_L_Thumb01"],
	"左親指１": ["cf_J_Hand_Thumb02_L", "mixamorig:LeftHandThumb2", "ValveBiped.Bip01_L_Finger01", "bip_thumb_1_L", "SK_L_Thumb02"],
	"左親指２": ["cf_J_Hand_Thumb03_L", "mixamorig:LeftHandThumb3", "ValveBiped.Bip01_L_Finger02", "bip_thumb_2_L", "SK_L_Thumb03"]
}

arm_dict = {
	"右肩": ["cf_s_shoulder02_R", "cf_J_Shoulder02_s_R", "mixamorig:RightShoulder", "ValveBiped.Bip01_R_Clavicle", "bip_collar_R", "SK_R_Shoulder", "cf_d_shoulder_R", "cf_j_shoulder_R", "cf_s_shoulder02_R", "a_n_shoulder_R", "k_f_shoulderR_00", "k_f_shoulderR_01", "k_f_shoulderR_02", "k_f_shoulderR_03", "cf_hit_shoulder_R"],
	"右腕": ["cf_s_arm01_R", "cf_s_arm02_R", "cf_s_arm03_R", "cf_J_ArmUp01_s_R", "mixamorig:RightArm", "ValveBiped.Bip01_R_UpperArm", "bip_upperArm_R", "RF_R_ArmNoTwist", "RF_R_Arm_00", "RF_R_Arm_01", "SK_R_Arm", "cf_d_arm01_R", "cf_s_arm01_R", "cf_d_arm02_R", "cf_s_arm02_R", "a_n_arm_R", "k_f_armupR_00", "k_f_armupR_01", "k_f_armupR_02", "k_f_armupR_03", "KK_Colliders_cf_s_arm02_R", "cf_d_arm03_R", "cf_s_arm03_R", "cf_hit_arm_R"],
	"右ひじ": ["cf_s_forearm01_R", "cf_s_wrist_R", "cf_s_forearm02_R", "cf_J_ArmLow01_s_R", "mixamorig:RightForeArm", "ValveBiped.Bip01_R_Forearm", "bip_lowerArm_R", "SK_R_ForeArm", "RF_R_ForeArm_00", "RF_R_ForeArm_01", "cf_d_forearm02_R", "cf_s_forearm02_R", "cf_hit_wrist_R", "KK_Colliders_cf_s_forearm02_R", "cf_d_wrist_R", "cf_s_wrist_R", "cf_s_wrist_R", "a_n_wrist_R", "cf_d_hand_R", "cf_s_forearm01_R"],
	"右手首": ["cf_s_hand_R", "cf_d_hand_R", "cf_J_Hand_s_R", "mixamorig:RightHand", "ValveBiped.Bip01_R_Hand", "bip_hand_R", "SK_R_Hand", "cf_s_hand_R", "a_n_hand_R"],
	
	"左肩": ["cf_s_shoulder02_L", "cf_J_Shoulder02_s_L", "mixamorig:LeftShoulder", "ValveBiped.Bip01_L_Clavicle", "bip_collar_L", "SK_L_Shoulder", "cf_d_shoulder_L", "cf_j_shoulder_L", "cf_s_shoulder02_L", "a_n_shoulder_L", "k_f_shoulderL_00", "k_f_shoulderL_01", "k_f_shoulderL_02", "k_f_shoulderL_03", "cf_hit_shoulder_L"],
	"左腕": ["cf_s_arm01_L", "cf_s_arm02_L", "cf_s_arm03_L", "cf_J_ArmUp01_s_L", "mixamorig:LeftArm", "ValveBiped.Bip01_L_UpperArm", "bip_upperArm_L", "RF_L_ArmNoTwist", "RF_L_Arm_00", "RF_L_Arm_01", "SK_L_Arm", "cf_d_arm01_L", "cf_s_arm01_L", "cf_d_arm02_L", "cf_s_arm02_L", "a_n_arm_L", "k_f_armupL_00", "k_f_armupL_01", "k_f_armupL_02", "k_f_armupL_03", "KK_Colliders_cf_s_arm02_L", "cf_d_arm03_L", "cf_s_arm03_L", "cf_hit_arm_L"],
	"左ひじ": ["cf_s_forearm01_L", "cf_s_wrist_L", "cf_s_forearm02_L", "cf_J_ArmLow01_s_L", "mixamorig:LeftForeArm", "ValveBiped.Bip01_L_Forearm", "bip_lowerArm_L", "SK_L_ForeArm", "RF_L_ForeArm_00", "RF_L_ForeArm_01", "cf_d_forearm02_L", "cf_s_forearm02_L", "cf_hit_wrist_L", "KK_Colliders_cf_s_forearm02_L", "cf_d_wrist_L", "cf_s_wrist_L", "cf_s_wrist_L", "a_n_wrist_L", "cf_d_hand_L", "cf_s_forearm01_L"],
	"左手首": ["cf_s_hand_L", "cf_d_hand_L", "cf_J_Hand_s_L", "mixamorig:LeftHand", "ValveBiped.Bip01_L_Hand", "bip_hand_L", "SK_L_Hand", "cf_s_hand_L", "a_n_hand_L"]
}

leg_dict = {
	"右足": ["cf_s_thigh01_R", "cf_s_thigh02_R", "cf_s_thigh03_R", "cf_J_LegUp01_s_R", "mixamorig:RightUpLeg", "ValveBiped.Bip01_R_Thigh", "bip_hip_R", "SK_R_UpLeg", "RF_R_UpLeg_00", "RF_R_UpLeg_01", "cf_d_thigh01_R", "cf_s_thigh01_R", "cf_hit_thigh01_R", "k_f_legupR_00", "k_f_legupR_01", "k_f_legupR_02", "k_f_legupR_03", "KK_Colliders_cf_s_thigh01_R", "KK_Colliders_cf_s_thigh01_R__2", "cf_d_thigh02_R", "cf_s_thigh02_R", "a_n_leg_R", "cf_hit_thigh02_R", "KK_Colliders_cf_s_thigh02_R", "cf_d_thigh03_R", "cf_s_thigh03_R"],
	"右ひざ": ["cf_s_leg01_R", "cf_s_leg02_R", "cf_s_leg03_R", "cf_J_LegLow01_s_R", "mixamorig:RightLeg", "ValveBiped.Bip01_R_Calf", "bip_knee_R", "SK_R_Leg", "RF_R_Leg_00", "RF_R_Leg_01", "cf_d_kneeF_R", "k_f_legkneeR_00", "k_f_legkneeR_01", "k_f_legkneeR_02", "k_f_legkneeR_03", "cf_d_leg02_R", "cf_s_leg02_R", "cf_d_leg03_R", "cf_s_leg03_R", "a_n_ankle_R", "k_f_ancleR_00", "k_f_ancleR_01", "k_f_ancleR_02", "k_f_ancleR_03", "cf_j_leg03_R", "cf_s_leg01_R"],
	"右足首": ["cf_J_Foot02_R", "mixamorig:RightFoot", "ValveBiped.Bip01_R_Foot", "bip_foot_R", "SK_R_Foot"],
	"右つま先": ["cf_J_Toes01_R", "mixamorig:RightToeBase", "ValveBiped.Bip01_R_Toe0", "bip_toe_R", "SK_R_Toes"],
	"左足": ["cf_J_LegUp01_s_L", "mixamorig:LeftUpLeg", "ValveBiped.Bip01_L_Thigh", "bip_hip_L", "SK_L_UpLeg", "RF_L_UpLeg_00", "RF_L_UpLeg_01", "cf_d_thigh01_L", "cf_s_thigh01_L", "cf_hit_thigh01_L", "k_f_legupL_00", "k_f_legupL_01", "k_f_legupL_02", "k_f_legupL_03", "KK_Colliders_cf_s_thigh01_L", "KK_Colliders_cf_s_thigh01_L__2", "cf_d_thigh02_L", "cf_s_thigh02_L", "a_n_leg_L", "cf_hit_thigh02_L", "KK_Colliders_cf_s_thigh02_L", "cf_d_thigh03_L", "cf_s_thigh03_L"],
	"左ひざ": ["cf_J_LegLow01_s_L", "mixamorig:LeftLeg", "ValveBiped.Bip01_L_Calf", "bip_knee_L", "SK_L_Leg", "RF_l_Leg_00", "RF_L_Leg_01", "cf_d_kneeF_L", "k_f_legkneeL_00", "k_f_legkneeL_01", "k_f_legkneeL_02", "k_f_legkneeL_03", "cf_d_leg02_L", "cf_s_leg02_L", "cf_d_leg03_L", "cf_s_leg03_L", "a_n_ankle_L", "k_f_ancleL_00", "k_f_ancleL_01", "k_f_ancleL_02", "k_f_ancleL_03", "cf_j_leg03_L", "cf_s_leg01_L"],
	"左足首": ["cf_J_Foot02_L", "mixamorig:LeftFoot", "ValveBiped.Bip01_L_Foot", "bip_foot_L", "SK_L_Foot"],
	"左つま先": ["cf_J_Toes01_L", "mixamorig:LeftToeBase", "ValveBiped.Bip01_L_Toe0", "bip_toe_L", "SK_L_Toes"]
}

body_dict = {
	# these lists are longer than usual because those bones are split up and we'll merge them later on
	"下半身": ["cf_s_waist02", "cf_J_Kosi01_s", "mixamorig:Hips", "ValveBiped.Bip01_Pelvis", "bip_pelvis", "ValveBiped.Bip01_Spine", "bip_spine_0", "SK_Hips", "cf_s_waist02"],
	"上半身": ["cf_s_waist01", "mixamorig:Spine", "ValveBiped.Bip01_Spine1", "bip_spine_1", "SK_Spine01", "cf_s_waist01", "a_n_waist", "a_n_waist_b", "a_n_waist_f", "a_n_waist_L", "a_n_waist_R", "cf_s_spine01", "k_f_spine01_00", "k_f_spine01_01", "k_f_spine01_02", "k_f_spine01_03", "cf_J_Spine01_s"],
	"上半身2": ["mixamorig:Spine1","ValveBiped.Bip01_Spine2", "bip_spine_2", "SK_Spine02", "cf_s_spine02", "k_f_spine02_00", "k_f_spine02_01", "k_f_spine02_02", "k_f_spine02_03", "cf_hit_spine02", "cf_J_Spine02_s"],
	"上半身3": ["mixamorig:Spine2", "cf_s_spine03", "k_f_spine03_00", "cf_hit_spine03", "k_f_spine03_01", "k_f_spine03_02", "k_f_spine03_03", "cf_hit_spine03_2","cf_J_Spine03_s"],
	"首": ["mixamorig:Neck", "ValveBiped.Bip01_Spine4", "bip_spine_3", "ValveBiped.Bip01_Neck1", "bip_neck", "SK_Neck", "cf_s_neck", "a_n_neck", "cf_J_Neck_s"],
	"頭": ["mixamorig:Head", "ValveBiped.Bip01_Head1", "bip_head", "SK_Head", "cf_s_head", "cf_J_Head_s"]
}

# base order: 上半身, 下半身, 腰, グルーブ, センター, 全ての親
# the rest of the work should be done in pmxeditor instead, jsut one click away


def main(moreinfo=True):
	# copied codes
	core.MY_PRINT_FUNC("Please enter name of PMX model file:")
	input_filename_pmx = core.MY_FILEPROMPT_FUNC(".pmx")
	
	# object
	pmx_file_obj: pmxstruct.Pmx = pmxlib.read_pmx(input_filename_pmx, moreinfo=moreinfo)
	
	# since there is an update to Valve Bip tools (I guess?), there is different bone names: the old and new one
	# only prefixes are changed along with order, thus there is a little bit scripting here to find the last leg
	big_dict: dict = {**body_dict, **leg_dict, **arm_dict, **finger_dict}
	
	#########################################################################
	# stage 1: create & insert core/base bones (grooves, mother,...)
	#########################################################################
	
	# base bone section
	# base order: 上半身, 下半身, 腰 (b_1), グルーブ, センター, 全ての親
	base_bone_4_name = "全ての親"  # motherbone
	base_bone_3_name = "センター"  # center
	base_bone_2_name = "グルーブ"  # groove
	base_bone_1_name = "腰"  # waist
	
	# note: Source models apparently have a much larger scale than MMD models
	base_bone_4_pos = [0, 0, 0]
	base_bone_3_pos = [0, 21, -0.533614993095398]
	base_bone_2_pos = base_bone_3_pos
	base_bone_1_pos = [0, 32, -0.533614993095398]
	
	# pelvis_pos = [-4.999999873689376e-06, 38.566917419433594, -0.533614993095398]
	
	# 全ての親, name_en, [0.0, 0.0, -0.4735046625137329], -1, 0, False,
	# True, True, True, True,
	# False, [0.0, 0.0, 0.0], False, False, None,
	# None, False, None, False, None, None, False, None, False,
	# None, None, None, None
	
	# base order: 上半身, 下半身, 腰 (b_1), グルーブ, センター, 全ての親
	base_bone_4_obj = pmxstruct.PmxBone(
		name_jp=base_bone_4_name, name_en="", pos=base_bone_4_pos, parent_idx=-1, deform_layer=0,
		deform_after_phys=False, has_rotate=True, has_translate=True, has_visible=True, has_enabled=True,
		has_ik=False, tail_usebonelink=False, tail=[0, 3, 0], inherit_rot=False, inherit_trans=False,
		has_fixedaxis=False, has_localaxis=False, has_externalparent=False,
	)
	insert_single_bone(pmx_file_obj, base_bone_4_obj, 0)
	
	base_bone_3_obj = pmxstruct.PmxBone(
		name_jp=base_bone_3_name, name_en="", pos=base_bone_3_pos, parent_idx=0, deform_layer=0,
		deform_after_phys=False, has_rotate=True, has_translate=True, has_visible=True, has_enabled=True,
		has_ik=False, tail_usebonelink=False, tail=[0, -3, 0], inherit_rot=False, inherit_trans=False,
		has_fixedaxis=False, has_localaxis=False, has_externalparent=False,
	)
	insert_single_bone(pmx_file_obj, base_bone_3_obj, 1)
	
	base_bone_2_obj = pmxstruct.PmxBone(
		name_jp=base_bone_2_name, name_en="", pos=base_bone_2_pos, parent_idx=1, deform_layer=0,
		deform_after_phys=False, has_rotate=True, has_translate=True, has_visible=True, has_enabled=True,
		has_ik=False, tail_usebonelink=False, tail=[0, 0, 1.5], inherit_rot=False, inherit_trans=False,
		has_fixedaxis=False, has_localaxis=False, has_externalparent=False,
	)
	insert_single_bone(pmx_file_obj, base_bone_2_obj, 2)
	
	base_bone_1_obj = pmxstruct.PmxBone(
		name_jp=base_bone_1_name, name_en="", pos=base_bone_1_pos, parent_idx=2, deform_layer=0,
		deform_after_phys=False, has_rotate=True, has_translate=True, has_visible=True, has_enabled=True,
		has_ik=False, tail_usebonelink=False, tail=[0, 0, 0], inherit_rot=False, inherit_trans=False,
		has_fixedaxis=False, has_localaxis=False, has_externalparent=False,
	)
	insert_single_bone(pmx_file_obj, base_bone_1_obj, 3)
	
	#########################################################################
	# phase 2: translate Source names to MMD names
	#########################################################################
	
	# for each mapping of source-name to mmd-name,
	for mmd_name, source_possible_names in big_dict.items():
		# for each bone,
		for index, bone_object in enumerate(pmx_file_obj.bones):
			# if it has a source-name, replace with mmd-name
			if bone_object.name_jp in source_possible_names:
				pmx_file_obj.bones[index].name_jp = mmd_name
	
	# next, fix the lowerbody bone
	# find lowerbod
	lowerbod_obj = core.my_list_search(pmx_file_obj.bones, lambda x: x.name_jp == "下半身", getitem=True)
	# elif bone_object.name_jp in ["ValveBiped.Bip01_Pelvis", "bip_pelvis"]:
	if lowerbod_obj is not None:
		# should not be translateable
		lowerbod_obj.has_translate = False
		# parent should be waist
		lowerbod_obj.parent_idx = 3
	# next, fix the upperbody bone
	upperbod_obj = core.my_list_search(pmx_file_obj.bones, lambda x: x.name_jp == "上半身", getitem=True)
	if upperbod_obj is not None:
		# should not be translateable
		upperbod_obj.has_translate = False
		# parent should be waist
		upperbod_obj.parent_idx = 3
	
	
	#########################################################################
	# phase 3: create & insert IK bones for leg/toe
	#########################################################################
	# find the last leg item index
	# when creating IK bones, want to insert the IK bones after both legs
	r_l_index = core.my_list_search(pmx_file_obj.bones, lambda x: x.name_jp == "右足")
	r_k_index = core.my_list_search(pmx_file_obj.bones, lambda x: x.name_jp == "右ひざ")
	r_a_index = core.my_list_search(pmx_file_obj.bones, lambda x: x.name_jp == "右足首")
	r_t_index = core.my_list_search(pmx_file_obj.bones, lambda x: x.name_jp == "右つま先")
	l_l_index = core.my_list_search(pmx_file_obj.bones, lambda x: x.name_jp == "左足")
	l_k_index = core.my_list_search(pmx_file_obj.bones, lambda x: x.name_jp == "左ひざ")
	l_a_index = core.my_list_search(pmx_file_obj.bones, lambda x: x.name_jp == "左足首")
	l_t_index = core.my_list_search(pmx_file_obj.bones, lambda x: x.name_jp == "左つま先")
	# if somehow they aren't found, default to 0
	if r_l_index is None: r_l_index = 0
	if r_k_index is None: r_k_index = 0
	if r_a_index is None: r_a_index = 0
	if r_t_index is None: r_t_index = 0
	if l_l_index is None: l_l_index = 0
	if l_k_index is None: l_k_index = 0
	if l_a_index is None: l_a_index = 0
	if l_t_index is None: l_t_index = 0
	
	if r_t_index > l_t_index:
		last_leg_item_index = r_t_index
	else:
		last_leg_item_index = l_t_index
	
	leg_left_ik_name = "左足ＩＫ"
	leg_left_toe_ik_name = "左つま先ＩＫ"
	leg_right_ik_name = "右足ＩＫ"
	leg_right_toe_ik_name = "右つま先ＩＫ"
	
	# these limits in degrees
	knee_limit_1 = [-180, 0.0, 0.0]
	knee_limit_2 = [-0.5, 0.0, 0.0]
	# other parameters
	ik_loops = 40
	ik_toe_loops = 8
	ik_angle = 114.5916  # degrees, =2 radians
	ik_toe_angle = 229.1831  # degrees, =4 radians
	
	# adding IK and such
	leg_left_ankle_obj = pmx_file_obj.bones[l_a_index]
	leg_left_toe_obj = pmx_file_obj.bones[l_t_index]
	leg_right_ankle_obj = pmx_file_obj.bones[r_a_index]
	leg_right_toe_obj = pmx_file_obj.bones[r_t_index]
	
	leg_left_ankle_pos = leg_left_ankle_obj.pos
	leg_left_toe_pos = leg_left_toe_obj.pos
	leg_right_ankle_pos = leg_right_ankle_obj.pos
	leg_right_toe_pos = leg_right_toe_obj.pos
	
	# toe /// places of some value wont match with the struct /// taken from hololive's korone model
	# name, name, [-0.823277473449707, 0.2155265510082245, -1.8799238204956055], 112, 0, False,
	# True, True, True, True,
	# False, [0.0, -1.3884940147399902, 1.2653569569920364e-07] /// This is offset, False, False, None,
	# None, False, None, False, None, None, False, None, True,
	# 111, 160, 1.0, [[110, None, None]]
	
	# leg
	# 右足ＩＫ, en_name, [-0.8402935862541199, 1.16348397731781, 0.3492986857891083], 0, 0, False,
	# True, True, True, True,
	# False, [0.0, -2.53071505085245e-07, 1.3884940147399902], False, False, None,
	# None, False, None, False, None, None, False, None, True,
	# 110, 85, 1.9896754026412964, [[109, [-3.1415927410125732, 0.0, 0.0], [-0.008726646192371845, 0.0, 0.0]]
	# /// These ik_links are in radians /// , [108, None, None]]
	
	leg_left_ik_obj = pmxstruct.PmxBone(
		name_jp=leg_left_ik_name, name_en="", pos=leg_left_ankle_pos, parent_idx=0, deform_layer=0,
		deform_after_phys=False, has_rotate=True, has_translate=True, has_visible=True, has_enabled=True,
		has_ik=True, tail_usebonelink=False, tail=[0.0, 0.0, 1.0], inherit_rot=False, inherit_trans=False,
		has_fixedaxis=False, has_localaxis=False, has_externalparent=False,
		ik_target_idx=l_a_index, ik_numloops=ik_loops, ik_angle=ik_angle,
		ik_links=[pmxstruct.PmxBoneIkLink(idx=l_k_index, limit_min=knee_limit_1, limit_max=knee_limit_2),
				  pmxstruct.PmxBoneIkLink(idx=l_l_index)],
	)
	insert_single_bone(pmx_file_obj, leg_left_ik_obj, last_leg_item_index + 1)
	
	leg_left_toe_ik_obj = pmxstruct.PmxBone(
		name_jp=leg_left_toe_ik_name, name_en="", pos=leg_left_toe_pos, parent_idx=last_leg_item_index + 1, deform_layer=0,
		deform_after_phys=False, has_rotate=True, has_translate=True, has_visible=True, has_enabled=True,
		has_ik=True, tail_usebonelink=False, tail=[0.0, -1.0, 0.0], inherit_rot=False, inherit_trans=False,
		has_fixedaxis=False, has_localaxis=False, has_externalparent=False,
		ik_target_idx=l_t_index, ik_numloops=ik_toe_loops, ik_angle=ik_toe_angle,
		ik_links=[pmxstruct.PmxBoneIkLink(idx=l_a_index)],
	)
	insert_single_bone(pmx_file_obj, leg_left_toe_ik_obj, last_leg_item_index + 2)
	
	leg_right_ik_obj = pmxstruct.PmxBone(
		name_jp=leg_right_ik_name, name_en="", pos=leg_right_ankle_pos, parent_idx=0, deform_layer=0,
		deform_after_phys=False, has_rotate=True, has_translate=True, has_visible=True, has_enabled=True,
		has_ik=True, tail_usebonelink=False, tail=[0.0, 0.0, 1.0], inherit_rot=False, inherit_trans=False,
		has_fixedaxis=False, has_localaxis=False, has_externalparent=False,
		ik_target_idx=r_a_index, ik_numloops=ik_loops, ik_angle=ik_angle,
		ik_links=[pmxstruct.PmxBoneIkLink(idx=r_k_index, limit_min=knee_limit_1, limit_max=knee_limit_2),
				  pmxstruct.PmxBoneIkLink(idx=r_l_index)],
	)
	insert_single_bone(pmx_file_obj, leg_right_ik_obj, last_leg_item_index + 3)
	
	leg_right_toe_ik_obj = pmxstruct.PmxBone(
		name_jp=leg_right_toe_ik_name, name_en="", pos=leg_right_toe_pos, parent_idx=last_leg_item_index + 3, deform_layer=0,
		deform_after_phys=False, has_rotate=True, has_translate=True, has_visible=True, has_enabled=True,
		has_ik=True, tail_usebonelink=False, tail=[0.0, -1.0, 0.0], inherit_rot=False, inherit_trans=False,
		has_fixedaxis=False, has_localaxis=False, has_externalparent=False,
		ik_target_idx=r_t_index, ik_numloops=ik_toe_loops, ik_angle=ik_toe_angle,
		ik_links=[pmxstruct.PmxBoneIkLink(idx=r_a_index)],
	)
	insert_single_bone(pmx_file_obj, leg_right_toe_ik_obj, last_leg_item_index + 4)
	
	# output the file
	output_filename_pmx = input_filename_pmx[0:-4] + "_RenamedBones.pmx"
	pmxlib.write_pmx(output_filename_pmx, pmx_file_obj, moreinfo=moreinfo)
	core.MY_PRINT_FUNC("Done!")
	return None


if __name__ == "__main__":
	# copied from bone_armik_addremove
	try:
		# print info to explain the purpose of this file
		core.MY_PRINT_FUNC(helptext)
		core.MY_PRINT_FUNC("")
		
		main()
		core.pause_and_quit("Done with everything! Goodbye!")
	except (KeyboardInterrupt, SystemExit):
		# this is normal and expected, do nothing and die normally
		pass
	except Exception as ee:
		# if an unexpected error occurs, catch it and print it
		# and call pause_and_quit so the window stays open for a bit
		core.MY_PRINT_FUNC(ee.__class__.__name__, ee)
		core.pause_and_quit(
			"ERROR: something truly strange and unexpected has occurred, sorry, good luck figuring out what tho")