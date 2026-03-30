package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class SideSpecial_Air__44 extends MovieClip
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
        public var proj:*;

        public function SideSpecial_Air__44()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 11, this.frame12, 12, this.frame13, 31, this.frame32, 32, this.frame33, 40, this.frame41, 42, this.frame43, 56, this.frame57);
        }

        public function toGround(_arg_1:*=null):*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toGround);
            this.self.removeEventListener(SSF2Event.CHAR_GRAB, this.toThrow);
            this.self.setGlobalVariable("LucarioSSpecFrame", currentFrame);
            this.self.setGlobalVariable("LucarioSSpecProj", this.proj);
            this.self.forceAttack("b_forward", null, true);
        }

        public function toThrow(_arg_1:*=null):*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toGround);
            this.self.removeEventListener(SSF2Event.CHAR_GRAB, this.toThrow);
            this.self.updateAttackStats({"air_ease":0});
            SSF2API.playSound("grab");
            this.self.stancePlayFrame("throw");
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

        public function killProj(_arg_1:*=null):*
        {
            if (!(this.proj.isDisposed()) && (this.self.getCurrentAnimation() != "b_forward"))
            {
                this.proj.destroy();
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.updateAuraDamage([1]);
                this.self.updateAuraPaws();
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toGround);
                this.self.addEventListener(SSF2Event.CHAR_GRAB, this.toThrow);
            };
        }

        internal function frame2():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame12():*
        {
            this.proj = this.self.fireProjectile("forcepalm");
            this.self.swapDepths(this.proj);
            this.self.addEventListener(SSF2Event.STATE_CHANGE, this.killProj);
            this.self.playVoiceSound(1);
        }

        internal function frame13():*
        {
            this.fireSound();
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
            this.self.updateAttackStats({"air_ease":-1});
        }

        internal function frame43():*
        {
            this.self.playVoiceSound(2);
            this.fireSound();
            this.self.updateAuraPaws();
        }

        internal function frame57():*
        {
            this.self.endAttack();
        }


    }
}

