#!/usr/bin/env python3

import sys

from gvm.protocols.gmp.requests.v226 import EntityType, PermissionSubjectType

import moregvm

PAGESIZE = 25


class GbMakeAllVisibleFor(moregvm.Tool):
    """
    Make ALL resources of a given type that the current user owns visible to a principal.

    Example:
        $ gb_make_all_visible_for override group 72dbb441-8c96-41b4-939d-7bfc28dd6e6d
    """

    @classmethod
    def required_args(cls):
        return {
            "resource_type": "Type of resource (override or note)",
            "principal_type": "Type of subject principal (user, group, role)",
            "principal_id": "UUID of the subject user, group or role",
        }

    @classmethod
    def toggles(cls):
        return {
            "debug": "Print debugging messages",
            "really-change": "Actually change state instead of a dry run",
        }

    def _find_all_resource_ids(self, restype: str, username: str) -> set[str]:
        ids = set()

        filter_string = f'sort=uuid owner={username}'
        getter = getattr(self.gmp, f'get_{restype}s')

        totalcount_resp = getter(filter_string='rows=1 ' + filter_string)
        totalcount = int(totalcount_resp.find(f"./{restype}_count/filtered").text)

        pos = 1
        tcnt_errmsg = ''
        while pos <= totalcount:
            pagination = f"rows={PAGESIZE} first={pos}"
            pos += PAGESIZE

            resources = getter(filter_string=pagination + " " + filter_string, details=False, result=False)
            resource_list = resources.xpath(f"./{restype}")

            current_totalcount = int(resources.find(f"./{restype}_count/filtered").text)
            if totalcount != current_totalcount:
                tcnt_errmsg += f' to {current_totalcount}'

            for resource in resource_list:
                if self.args["debug"]: print(f"saw {restype} {resource.attrib['id']}")
                ids.add(resource.attrib['id'])

        if tcnt_errmsg:
            raise moregvm.TemporaryError(f'Total count of {restype}s changed from {totalcount}{tcnt_errmsg} during execution. Results are probably inconsistent. Aborting.')

        return ids

    def tool_main(self) -> None:
        username = self.user
        really_change = self.args["really_change"]
        debug = self.args["debug"]
        principal_id = self.args["principal_id"]
        principal_type = self.args["principal_type"]
        resource_type = self.args["resource_type"]
        enum_principal_type = PermissionSubjectType(principal_type)
        enum_resource_type = EntityType(resource_type)

        if resource_type not in {"override", "note"}:
            raise moregvm.PermanentError('Currently only the types "override" and "note" are supported')

        resource_ids = self._find_all_resource_ids(resource_type, username)
        resources_with_permission = set()
        perm_map = {} # {permission_id: resource_id}

        filter_string = f'sort=uuid owner={username} and type={resource_type} and subject_type={principal_type} and subject_uuid={principal_id}'

        totalcount_resp = self.gmp.get_permissions(filter_string='rows=1 ' + filter_string)
        totalcount = int(totalcount_resp.find("./permission_count/filtered").text)

        pos = 1
        tcnt_errmsg = ''
        while pos <= totalcount:
            pagination = f"rows={PAGESIZE} first={pos}"
            pos += PAGESIZE

            permissions = self.gmp.get_permissions(filter_string=pagination + " " + filter_string)
            permission_list = permissions.xpath("./permission")

            current_totalcount = int(permissions.find("./permission_count/filtered").text)
            if totalcount != current_totalcount:
                tcnt_errmsg += f' to {current_totalcount}'

            for permission in permission_list:
                if debug: print(f"saw permission {permission.attrib['id']} for {permission.find('./subject/type').text} '{permission.find('./subject/name').text}'({permission.find('./subject').attrib['id']}) on {permission.find('./resource/type').text} {permission.find('./resource').attrib['id']}")
                if not permission.find('./owner/name').text == username:
                    raise moregvm.PermanentError(f'Permission search returned permission that belongs to someone else')
                if not permission.find('./resource/type').text == resource_type:
                    raise moregvm.PermanentError(f'Permission search returned permission for incorrect resource type')
                if not permission.find('./subject/type').text == principal_type:
                    raise moregvm.PermanentError(f'Permission search returned permission for incorrect principal type')
                if not permission.find('./subject').attrib['id'] == principal_id:
                    raise moregvm.PermanentError(f'Permission search returned permission for incorrect principal id')
                resources_with_permission.add(permission.find('./resource').attrib['id'])
                perm_map[permission.attrib['id']] = permission.find('./resource').attrib['id']

        if tcnt_errmsg:
            raise moregvm.TemporaryError(f'Total count of permissions changed from {totalcount}{tcnt_errmsg} during execution. Results are probably inconsistent. Aborting.')

        if not really_change:
            print('Dry run, would change:')
        if debug:
            for resid in resource_ids.intersection(resources_with_permission):
                # everything ok, debug only:
                print(f'  no change: {resource_type} {resid}')
        for resid in resource_ids - resources_with_permission:
            # missing permission
            if debug or not really_change:
                print(f'  create_permission get_{resource_type}s on {resource_type} {resid} for {principal_type} {principal_id}')
            if really_change:
                self.gmp.create_permission(f'get_{resource_type}s', principal_id, enum_principal_type, resource_id=resid, resource_type=enum_resource_type, comment='autocreated by gb_make_all_visible_for')
        for permid, resid in perm_map.items():
            if resid not in resource_ids:
                # permission referring to missing resource (deleted)
                if debug or not really_change:
                    print(f'  delete_permission {permid}')
                if really_change:
                    self.gmp.delete_permission(permid)
        if not really_change:
            print('Re-run with --really-change to apply the above changes (if any).')


if __name__ == '__main__':
    GbMakeAllVisibleFor.run_from_sysargs()
