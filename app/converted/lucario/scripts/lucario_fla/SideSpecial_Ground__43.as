package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class SideSpecial_Ground__43 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var grabBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var touchBox:MovieClip;
        public var self:LucarioExt;
        public var curFrame:int;
        public var proj:*;

        public function SideSpecial_Ground__43()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 11, this.frame12, 12, this.frame13, 31, this.frame32, 32, this.frame33, 40, this.frame41, 42, this.frame43, 56, this.frame57);
        }

        public function toThrow(_arg_1:*=null):*
        {
            this.self.removeEventListener(SSF2Event.CHAR_GRAB, this.toThrow);
            SSF2API.playSound("grab");
            this.self.stancePlayFrame("throw");
        }

        public function killProj(_arg_1:*=null):*
        {
            if (!this.proj.isDisposed())
            {
                this.proj.destroy();
            };
        }

        public function fireSound():*
        {
            if (this.self.auraPercentage < 0.3)
            {
                this.self.playSound("lucario_sspec_s");
            }
            else if (this.self.auraPercentage < 0.6)
            {
                this.self.playSound("lucario_sspec_m");
            }
            else
            {
                this.self.playSound("lucario_sspec_l");
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (SSF2API.isReady() && this.self)
            {
                this.curFrame = this.self.getGlobalVariable("LucarioSSpecFrame");
                this.self.setGlobalVariable("LucarioSSpecFrame", 0);
                this.proj = this.self.getGlobalVariable("LucarioSSpecProj");
                this.self.setGlobalVariable("LucarioSSpecProj", null);
                this.self.updateAuraDamage([1]);
                this.self.updateAuraPaws();
                this.self.addEventListener(SSF2Event.CHAR_GRAB, this.toThrow);
                if (this.curFrame > 1)
                {
                    if (this.proj != null)
                    {
                        this.self.addEventListener(SSF2Event.STATE_CHANGE, this.killProj);
                    };
                    this.self.stancePlayFrame(this.curFrame);
                };
            };
        }

        internal function frame2():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.playAttackSound(1);
            };
        }

        internal function frame12():*
        {
            if (this.curFrame != currentFrame)
            {
                this.proj = this.self.fireProjectile("forcepalm");
                this.self.swapDepths(this.proj);
                this.self.addEventListener(SSF2Event.STATE_CHANGE, this.killProj);
                this.self.playVoiceSound(1);
            };
        }

        internal function frame13():*
        {
            if (this.curFrame != currentFrame)
            {
                this.fireSound();
            };
            this.self.attachEffect("global_dust_heavy");
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m2");
            }
            else
            {
                this.self.playSound("lucario_step2");
            };
        }

        internal function frame32():*
        {
            this.self.endAttack();
        }

        internal function frame33():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame41():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_l2");
            }
            else
            {
                this.self.playSound("lucario_step2");
            };
        }

        internal function frame43():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.playVoiceSound(2);
                this.fireSound();
                this.self.updateAuraPaws();
            };
        }

        internal function frame57():*
        {
            this.self.endAttack();
        }


    }
}

