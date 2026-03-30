package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class ForwardTilt_32 extends MovieClip
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

        public function ForwardTilt_32()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 5, this.frame6, 10, this.frame11, 11, this.frame12, 17, this.frame18, 19, this.frame20);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (SSF2API.isReady() && this.self)
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
                this.self.updateAuraDamage([1]);
                this.self.updateAuraPaws();
            };
        }

        internal function frame5():*
        {
            this.self.addEffectToList(this.self.attachEffect("trail_lucario_ftilt", {
                "scaleX":1.15,
                "scaleY":1.15,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m1");
            }
            else
            {
                this.self.playSound("lucario_step1");
            };
        }

        internal function frame6():*
        {
            this.self.playAttackSound(1);
            this.self.updateAttackBoxStats(1, {
                "damage":(11 * this.self.auraMultiplier),
                "hitStun":4,
                "selfHitStun":2,
                "direction":20,
                "power":52,
                "kbConstant":68,
                "effectSound":"lucario_hit_ml",
                "aura":true
            });
            this.self.updateAttackBoxStats(2, {
                "damage":(11 * this.self.auraMultiplier),
                "hitStun":4,
                "selfHitStun":2,
                "direction":20,
                "power":52,
                "kbConstant":68,
                "effectSound":"lucario_hit_ml",
                "aura":true
            });
            this.self.refreshAttackID();
            this.self.updateAuraPaws();
            this.self.attachEffect("global_dust_light");
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

        internal function frame11():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame12():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame18():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame20():*
        {
            this.self.endAttack();
        }


    }
}

