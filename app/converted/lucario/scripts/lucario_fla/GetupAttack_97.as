package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class GetupAttack_97 extends MovieClip
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

        public function GetupAttack_97()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 7, this.frame8, 8, this.frame9, 11, this.frame12, 13, this.frame14, 19, this.frame20, 24, this.frame25);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (SSF2API.isReady() && this.self)
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
                this.self.setIntangibility(true);
                this.self.updateAuraPaws();
            };
        }

        internal function frame5():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m2");
            }
            else
            {
                this.self.playSound("lucario_step2");
            };
        }

        internal function frame8():*
        {
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

        internal function frame9():*
        {
            this.self.playAttackSound(1);
            this.self.addEffectToList(this.self.attachEffect("trail_lucario_getup1", {
                "scaleX":1.15,
                "scaleY":1.15,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.addEffectToList(this.self.pushEffectBehind(this.self.attachEffect("trail_lucario_getup2", {
                "scaleX":1.15,
                "scaleY":1.15,
                "parentLock":true,
                "syncHitStun":true
            })));
            this.self.clearEffectsOnStateChange();
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame12():*
        {
            this.self.playAttackSound(1);
            this.self.updateAuraPaws();
        }

        internal function frame14():*
        {
            this.self.setIntangibility(false);
            this.self.updateAuraPaws();
        }

        internal function frame20():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m1");
            }
            else
            {
                this.self.playSound("lucario_step1");
            };
            this.self.updateAuraPaws();
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}

