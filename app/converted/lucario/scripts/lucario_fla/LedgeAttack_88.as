package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class LedgeAttack_88 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;
        public var playsound:Number;
        public var audio:Number;

        public function LedgeAttack_88()
        {
            super();
            addFrameScript(0, this.frame1, 3, this.frame4, 6, this.frame7, 9, this.frame10, 11, this.frame12, 12, this.frame13, 22, this.frame23, 24, this.frame25);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setIntangibility(true);
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
                this.self.updateAuraPaws();
            };
        }

        internal function frame4():*
        {
            this.self.updateAuraPaws();
            this.self.playSound("lucario_jump1");
        }

        internal function frame7():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame10():*
        {
            this.self.setXSpeed(10, false);
            this.self.addEffectToList(this.self.attachEffect("trail_lucario_ledge", {
                "scaleX":1.15,
                "scaleY":1.15,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame12():*
        {
            this.self.attachEffect("global_dust_light");
            this.self.playAttackSound(1);
            if ((this.playsound > 0.2) && (this.playsound <= 0.4) && (this.audio != 1))
            {
                this.self.playVoiceSound(1);
                this.self.setGlobalVariable("audio", 1);
            };
            if ((this.playsound > 0.4) && (this.playsound <= 0.6) && (this.audio != 2))
            {
                this.self.playVoiceSound(2);
                this.self.setGlobalVariable("audio", 2);
            };
            if ((this.playsound > 0.6) && (this.playsound <= 0.8) && (this.audio != 3))
            {
                this.self.playVoiceSound(3);
                this.self.setGlobalVariable("audio", 3);
            };
            if ((this.playsound > 0.8) && (this.playsound <= 1) && (this.audio != 4))
            {
                this.self.playVoiceSound(4);
                this.self.setGlobalVariable("audio", 4);
            };
        }

        internal function frame13():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame23():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}

