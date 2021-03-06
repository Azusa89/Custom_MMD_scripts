# Nuthouse01 - 10/10/2020 - v5.03
# This code is free to use and re-distribute, but I cannot be held responsible for damages that it may or may not cause.
#####################

# first import system stuff
import os
from typing import List

# second, wrap custom imports with a try-except to catch it if files are missing
try:
	# these imports work if running from GUI
	from . import nuthouse01_core as core
	from . import nuthouse01_pmx_parser as pmxlib
	from . import nuthouse01_pmx_struct as pmxstruct
	from ._prune_unused_bones import delete_multiple_bones, insert_single_bone, apply_bone_remapping
	from ._prune_unused_vertices import delme_list_to_rangemap
except ImportError as eee:
	try:
		# these imports work if running from double-click on THIS script
		import nuthouse01_core as core
		import nuthouse01_pmx_parser as pmxlib
		import nuthouse01_pmx_struct as pmxstruct
		from _prune_unused_bones import delete_multiple_bones, insert_single_bone, apply_bone_remapping
		from _prune_unused_vertices import delme_list_to_rangemap
	except ImportError as eee:
		print(eee.__class__.__name__, eee)
		print("ERROR: failed to import some of the necessary files, all my scripts must be together in the same folder!")
		print("...press ENTER to exit...")
		input()
		exit()
		core = pmxlib = pmxstruct = delete_multiple_bones = insert_single_bone = delme_list_to_rangemap = apply_bone_remapping = None




# when debug=True, disable the catchall try-except block. this means the full stack trace gets printed when it crashes,
# but if launched in a new window it exits immediately so you can't read it.
DEBUG = False

helptext = '''=================================================
bone_armik_addremove:
This very simple script will generate "arm IK bones" if they do not exist, or delete them if they do exist.
The output suffix will be "_IK" if it added IK, or "_noIK" if it removed them.
'''

# copy arm/elbow/wrist, wrist is target of IK bone
# my improvement: make arm/elbow/wrist hidden and disabled
# ik has 20 loops, 45 deg, "左腕ＩＫ"
# original arm/elbow set to inherit 100% rot from their copies
# tricky: arm IK must be inserted between the shoulder and the arm, requires remapping all bone references ugh.
# if i use negative numbers for length, can I reuse the code for mass-delete?
# also add to dispframe

root="全ての親"
jp_left_arm =         "左腕"
jp_left_elbow =       "左ひじ"
jp_left_wrist =       "左手首"
jp_right_arm =        "右腕"
jp_right_elbow =      "右ひじ"
jp_right_wrist =      "右手首"
jp_sourcebones =   [jp_left_arm, jp_left_elbow, jp_left_wrist, jp_right_arm, jp_right_elbow, jp_right_wrist]
jp_l = "左"
jp_r = "右"
jp_arm =         "腕"
jp_elbow =       "ひじ"
jp_wrist =       "手首"
jp_thigh = "足"
jp_knee = "ひざ"
jp_upperbody = "上半身"  # this is used as the parent of the hand IK bone
jp_lowerbody = "下半身" 
jp_ikchainsuffix = "+" # appended to jp and en names of thew arm/elbow/wrist copies
jp_knee_IK= "ひざＩＫ"
jp_thigh_IK= "足ＩＫ"
jp_feet="足首"
jp_toe="つま先"
jp_feet_IK="つま先ＩＫ"

newik_loops = 20
newik_angle = 45

jp_newik = "手首ＩＫ"
jp_newik2 = "腕IK"  # for detecting only, always create with ^
en_newik = "armIK"
jp_newik3 = "ひじＩＫ"
en_newik2 = "elbowIK"
en_newik3 = "elbowIK"
en_lowerbody = "Pelvis"
jp_ik_dp = "IK"

pmx_yesik_suffix = " IK.pmx"
pmx_noik_suffix =  " no-IK.pmx"

endpoint_suffix_jp = "先"
endpoint_suffix_en = " end"

Knee_IK = "Knee IK"
Leg_IK = "Leg IK"
foot_IK = "Foot IK"

def main(moreinfo=True):
	# prompt PMX name
	core.MY_PRINT_FUNC("Please enter name of PMX input file:")
	input_filename_pmx = core.MY_FILEPROMPT_FUNC(".pmx")
	#input_filename_pmx = ("script test.pmx")
	pmx = pmxlib.read_pmx(input_filename_pmx, moreinfo=moreinfo)
	
	# detect whether arm ik exists
	r = core.my_list_search(pmx.bones, lambda x: x.name_jp == jp_r + jp_newik)
	if r is None:
		r = core.my_list_search(pmx.bones, lambda x: x.name_jp == jp_r + jp_newik2)
	l = core.my_list_search(pmx.bones, lambda x: x.name_jp == jp_l + jp_newik)
	if l is None:
		l = core.my_list_search(pmx.bones, lambda x: x.name_jp == jp_l + jp_newik2)

##Tim's Delete script~~	
	i = core.my_list_search(pmx.bones, lambda x: x.name_jp == jp_r + jp_thigh_IK)
	delete_multiple_bones(pmx,[i])
	i = core.my_list_search(pmx.bones, lambda x: x.name_jp == jp_l + jp_thigh_IK)
	delete_multiple_bones(pmx,[i])
	i = core.my_list_search(pmx.bones, lambda x: x.name_jp == jp_r + jp_feet_IK)
	delete_multiple_bones(pmx,[i])
	i = core.my_list_search(pmx.bones, lambda x: x.name_jp == jp_l + jp_feet_IK)
	delete_multiple_bones(pmx,[i])	

	# decide whether to create or remove arm ik
	if r is None and l is None:
		# add IK branch
		core.MY_PRINT_FUNC(">>>> Adding arm IK <<<")
		# set output name
		if input_filename_pmx.lower().endswith(pmx_noik_suffix.lower()):
			output_filename = input_filename_pmx[0:-(len(pmx_noik_suffix))] + pmx_yesik_suffix
		else:
			output_filename = input_filename_pmx[0:-4] + pmx_yesik_suffix
		for side in [jp_l, jp_r]:
			# first find all 3 arm bones
			# even if i insert into the list, this will still be a valid reference i think

			bones = []
			bones: List[pmxstruct.PmxBone]
			for n in [jp_arm, jp_elbow, jp_wrist, jp_thigh, jp_knee, jp_feet, jp_toe]:
				i = core.my_list_search(pmx.bones, lambda x: x.name_jp == side + n, getitem=True)
				if i is None:
					core.MY_PRINT_FUNC("ERROR1: semistandard bone '%s' is missing from the model, unable to create attached arm IK" % (side + n))
					raise RuntimeError()
				bones.append(i)
				#bones.append(jp_lowerbody)
			# get parent of arm bone (shoulder bone), new bones will be inserted after this
			shoulder_idx = bones[0].parent_idx
			#CUSTOM BONES PROGRESS HERE
			# new bones will be inserted AFTER shoulder_idx
			# newarm_idx = shoulder_idx+1
			# newelbow_idx = shoulder_idx+2
			# newwrist_idx = shoulder_idx+3
			# newik_idx = shoulder_idx+4
			
			# make copies of the 3 armchain bones
			
			# arm: parent is shoulder
			newarm = pmxstruct.PmxBone(
				name_jp=bones[0].name_jp + jp_ikchainsuffix, name_en=bones[0].name_en + jp_ikchainsuffix, 
				pos=bones[0].pos, parent_idx=shoulder_idx, deform_layer=bones[0].deform_layer, 
				deform_after_phys=bones[0].deform_after_phys,
				has_rotate=True, has_translate=False, has_visible=False, has_enabled=True, has_ik=False,
				tail_usebonelink=True, tail=0,  # want arm tail to point at the elbow, can't set it until elbow is created
				inherit_rot=False, inherit_trans=False,
				has_localaxis=bones[0].has_localaxis, localaxis_x=bones[0].localaxis_x, localaxis_z=bones[0].localaxis_z,
				has_externalparent=False, has_fixedaxis=False, 
			)
			insert_single_bone(pmx, newarm, shoulder_idx + 1)
			# change existing arm to inherit rot from this
			bones[0].inherit_rot = True
			bones[0].inherit_parent_idx = shoulder_idx + 1
			bones[0].inherit_ratio = 1
			
			# elbow: parent is newarm
			newelbow = pmxstruct.PmxBone(
				name_jp=bones[1].name_jp + jp_ikchainsuffix, name_en=bones[1].name_en + jp_ikchainsuffix, 
				pos=bones[1].pos, parent_idx=shoulder_idx+1, deform_layer=bones[1].deform_layer, 
				deform_after_phys=bones[1].deform_after_phys,
				has_rotate=True, has_translate=False, has_visible=False, has_enabled=True, has_ik=False,
				tail_usebonelink=True, tail=0,  # want elbow tail to point at the wrist, can't set it until wrist is created
				inherit_rot=False, inherit_trans=False,
				has_localaxis=bones[1].has_localaxis, localaxis_x=bones[1].localaxis_x, localaxis_z=bones[1].localaxis_z,
				has_externalparent=False, has_fixedaxis=False, 
			)
			insert_single_bone(pmx, newelbow, shoulder_idx + 2)
			# change existing elbow to inherit rot from this
			bones[1].inherit_rot = True
			bones[1].inherit_parent_idx = shoulder_idx + 2
			bones[1].inherit_ratio = 1
			# now that newelbow exists, change newarm tail to point to this
			newarm.tail = shoulder_idx + 2
			
			# wrist: parent is newelbow
			newwrist = pmxstruct.PmxBone(
				name_jp=bones[2].name_jp + jp_ikchainsuffix, name_en=bones[2].name_en + jp_ikchainsuffix, 
				pos=bones[2].pos, parent_idx=shoulder_idx+2, deform_layer=bones[2].deform_layer, 
				deform_after_phys=bones[2].deform_after_phys,
				has_rotate=True, has_translate=False, has_visible=False, has_enabled=True, has_ik=False,
				tail_usebonelink=True, tail=-1,  # newwrist has no tail
				inherit_rot=False, inherit_trans=False,
				has_localaxis=bones[2].has_localaxis, localaxis_x=bones[2].localaxis_x, localaxis_z=bones[2].localaxis_z,
				has_externalparent=False, has_fixedaxis=False, 
			)
			insert_single_bone(pmx, newwrist, shoulder_idx + 3)
			# now that newwrist exists, change newelbow tail to point to this
			newelbow.tail = shoulder_idx + 3
			
			# copy the wrist to make the IK bone
			en_suffix = "_L" if side == jp_l else "_R"
			# get index of "upperbody" to use as parent of hand IK bone
			ikpar = core.my_list_search(pmx.bones, lambda x: x.name_jp == jp_upperbody)
			mother = core.my_list_search(pmx.bones, lambda x: x.name_jp == root)
			if ikpar is None:
				core.MY_PRINT_FUNC("ERROR1: semistandard bone '%s' is missing from the model, unable to create attached arm IK" % jp_upperbody)
				raise RuntimeError()
			
			# newik = [side + jp_newik, en_newik + en_suffix] + bones[2][2:5] + [ikpar]  # new names, copy pos, new par
			# newik += bones[2][6:8] + [1, 1, 1, 1]  + [0, [0,1,0]] # copy deform layer, rot/trans/vis/en, tail type
			# newik += [0, 0, [], 0, [], 0, [], 0, []]  # no inherit, no fixed axis, no local axis, no ext parent, yes IK
			# # add the ik info: [is_ik, [target, loops, anglelimit, [[link_idx, []]], [link_idx, []]]] ] ]
			# newik += [1, [shoulder_idx+3, newik_loops, newik_angle, [[shoulder_idx+2,[]],[shoulder_idx+1,[]]] ] ]

			newik = pmxstruct.PmxBone(
				name_jp=side + jp_newik, name_en=en_newik + en_suffix, pos=bones[2].pos,
				parent_idx=ikpar, deform_layer=bones[2].deform_layer, deform_after_phys=bones[2].deform_after_phys,
				has_rotate=True, has_translate=True, has_visible=True, has_enabled=True,
				tail_usebonelink=False, tail=[0,1,0], inherit_rot=False, inherit_trans=False,
				has_fixedaxis=False, has_localaxis=False, has_externalparent=False, has_ik=True,
				ik_target_idx=shoulder_idx+3, ik_numloops=newik_loops, ik_angle=newik_angle,
				ik_links=[pmxstruct.PmxBoneIkLink(idx=shoulder_idx+2)]
			)
			insert_single_bone(pmx, newik, shoulder_idx + 4)

			newik = pmxstruct.PmxBone(
				name_jp=side + jp_newik3, name_en=en_newik2 + en_suffix, pos=bones[1].pos,
				parent_idx=ikpar, deform_layer=bones[2].deform_layer, deform_after_phys=bones[2].deform_after_phys,
				has_rotate=True, has_translate=True, has_visible=True, has_enabled=True,
				tail_usebonelink=False, tail=[0,1,0], inherit_rot=False, inherit_trans=False,
				has_fixedaxis=False, has_localaxis=False, has_externalparent=False, has_ik=True,
				ik_target_idx=shoulder_idx+2, ik_numloops=newik_loops, ik_angle=newik_angle,
				ik_links=[pmxstruct.PmxBoneIkLink(idx=shoulder_idx+1)]
			)
			insert_single_bone(pmx, newik, shoulder_idx + 4)

	##Leg bone insert##

			leg_idx = bones[6].parent_idx

			newfeetik = pmxstruct.PmxBone(
				name_jp=side + jp_feet_IK, name_en= foot_IK + en_suffix, pos=bones[6].pos,
				parent_idx=mother, deform_layer=bones[6].deform_layer, deform_after_phys=bones[2].deform_after_phys,
				has_rotate=True, has_translate=True, has_visible=True, has_enabled=True,
				tail_usebonelink=False, tail=[0,-1,0], inherit_rot=False, inherit_trans=False,
				has_fixedaxis=False, has_localaxis=False, has_externalparent=False, has_ik=True,
				ik_target_idx=leg_idx + 1, ik_numloops=newik_loops, ik_angle=newik_angle,
				ik_links=[pmxstruct.PmxBoneIkLink(idx=leg_idx)]
			)
			insert_single_bone(pmx, newfeetik, leg_idx + 1)


			newlegik = pmxstruct.PmxBone(
				name_jp=side + jp_thigh_IK, name_en= Leg_IK + en_suffix, pos=bones[5].pos,
				parent_idx=mother, deform_layer=bones[5].deform_layer, deform_after_phys=bones[2].deform_after_phys,
				has_rotate=True, has_translate=True, has_visible=True, has_enabled=True,
				tail_usebonelink=False, tail=[0,0,1], inherit_rot=False, inherit_trans=False,
				has_fixedaxis=False, has_localaxis=False, has_externalparent=False, has_ik=True,
				ik_target_idx=leg_idx, ik_numloops=newik_loops, ik_angle=newik_angle,
				ik_links=[pmxstruct.PmxBoneIkLink(idx=leg_idx -1)]
			)
			insert_single_bone(pmx, newlegik, leg_idx + 1)

			newkneeik = pmxstruct.PmxBone(
				name_jp=side + jp_knee_IK, name_en= Knee_IK + en_suffix, pos=bones[4].pos,
				parent_idx=mother, deform_layer=bones[4].deform_layer, deform_after_phys=bones[2].deform_after_phys,
				has_rotate=True, has_translate=True, has_visible=True, has_enabled=True,
				tail_usebonelink=False, tail=[0,0,1], inherit_rot=False, inherit_trans=False,
				has_fixedaxis=False, has_localaxis=False, has_externalparent=False, has_ik=True,
				ik_target_idx=leg_idx - 1, ik_numloops=newik_loops, ik_angle=newik_angle,
				ik_links=[pmxstruct.PmxBoneIkLink(idx=leg_idx -2)]
			)
			insert_single_bone(pmx, newkneeik, leg_idx + 1)

	pmxlib.write_pmx("temp.pmx", pmx)
	pmx = pmxlib.read_pmx("temp.pmx", moreinfo=True)

	# find the indexes of the bones we want to modify
	LfeetIKindex = core.my_list_search(pmx.bones, lambda x: x.name_jp == "左" + jp_feet_IK)
	RfeetIKindex = core.my_list_search(pmx.bones, lambda x: x.name_jp == "右" + jp_feet_IK)
	LthighIKindex = core.my_list_search(pmx.bones, lambda x: x.name_jp == "左" + jp_thigh_IK)
	RthighIKindex = core.my_list_search(pmx.bones, lambda x: x.name_jp == "右" + jp_thigh_IK)

	# Edit the feet parent_idx to the thighIK position.
	pmx.bones[LfeetIKindex].parent_idx=LthighIKindex
	pmx.bones[RfeetIKindex].parent_idx=RthighIKindex

	output_filename = core.get_unused_file_name(output_filename)
	pmxlib.write_pmx(output_filename, pmx, moreinfo=moreinfo)

	os.remove("temp.pmx")

	return None


if __name__ == '__main__':
	core.MY_PRINT_FUNC("Nuthouse01 - 10/10/2020 - v5.03")
	if DEBUG:
		# print info to explain the purpose of this file
		core.MY_PRINT_FUNC(helptext)
		core.MY_PRINT_FUNC("")
		
		main()
		core.pause_and_quit("Done with everything! Goodbye!")
	else:
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
			# if an unexpected error occurs, catch it and print it and call pause_and_quit so the window stays open for a bit
			core.MY_PRINT_FUNC(ee.__class__.__name__, ee)
			core.pause_and_quit("ERROR: something truly strange and unexpected has occurred, sorry, good luck figuring out what tho")
