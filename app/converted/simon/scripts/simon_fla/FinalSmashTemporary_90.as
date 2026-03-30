package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class FinalSmashTemporary_90 extends MovieClip
    {

        public var camBox:MovieClip;
        public var self:SimonExt;
        public var xframe:String;
        public var coffinProj:*;
        public var savedCameraSetting:Number;

        public function FinalSmashTemporary_90()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 13, this.frame14, 32, this.frame33, 46, this.frame47, 47, this.frame48, 49, this.frame50, 71, this.frame72, 72, this.frame73);
        }

        public function flipX(_arg_1:Number):Number
        {
            if (this.self.isFacingRight())
            {
                return _arg_1;
            };
            return _arg_1 * -1;
        }

        public function damageAllGrabbedOpponents():void
        {
            var _local_1:Array = this.self.getGrabbedOpponents();
            for (var _local_2:int = 0; _local_2 < _local_1.length; _local_2++)
            {
                if (_local_1[_local_2] && !(_local_1[_local_2].isDisposed()))
                {
                    _local_1[_local_2].takeDamage({
                        "damage":38,
                        "priority":7,
                        "hitStun":5,
                        "hitLag":-1,
                        "direction":60,
                        "power":30,
                        "kbConstant":100,
                        "shock":true,
                        "effectSound":"brawl_zap_l",
                        "bypassNonGrabbed":true,
                        "hasEffect":true
                    }, this.self);
                };
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
            this.xframe = null;
            this.coffinProj = null;
            this.savedCameraSetting = 360;
            if (parent && SSF2API.isReady() && this.self)
            {
                this.savedCameraSetting = SSF2API.getCamera().getCameraParameter("minZoomHeight");
                if (!this.self.getMetalStatus())
                {
                    this.self.playSound("ssf2_snd_vfx_simon_final_00", true);
                };
                this.self.camFocus(13);
                this.self.unnattachFromGround();
            };
        }

        internal function frame2():*
        {
            SSF2API.getCamera().updateCameraParameters({"minZoomHeight":70});
        }

        internal function frame14():*
        {
            this.self.attachEffect("global_sparkle", {
                "x":this.flipX(25),
                "y":-20
            });
            this.coffinProj = this.self.fireProjectile("simon_coffin");
            SSF2API.playSound(null);
            SSF2API.getCamera().updateCameraParameters({"minZoomHeight":this.savedCameraSetting});
        }

        internal function frame33():*
        {
            if (this.self.getGrabbedOpponents().length > 0)
            {
                this.self.stancePlayFrame("end2");
            };
        }

        internal function frame47():*
        {
            this.self.forceOnGround(5);
            if (!this.self.isOnGround())
            {
                this.self.updateAttackStats({"allowControl":true});
                this.self.resetJumps();
                this.self.toJump();
            };
        }

        internal function frame48():*
        {
            this.self.endAttack();
        }

        internal function frame50():*
        {
            if (((this.coffinProj != null) && !(this.coffinProj.isDisposed())) || this.self.getFinalSmashCutscene())
            {
                this.self.stancePlayFrame("end2");
            }
            else
            {
                this.damageAllGrabbedOpponents();
            };
        }

        internal function frame72():*
        {
            this.self.forceOnGround(5);
            if (!this.self.isOnGround())
            {
                this.self.updateAttackStats({"allowControl":true});
                this.self.resetJumps();
                this.self.toJump();
            };
        }

        internal function frame73():*
        {
            this.self.endAttack();
        }


    }
}

