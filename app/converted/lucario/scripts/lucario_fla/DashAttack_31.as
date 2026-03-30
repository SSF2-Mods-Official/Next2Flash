package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class DashAttack_31 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;
        public var playsound:Number;
        public var audio:Number;

        public function DashAttack_31()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 3, this.frame4, 4, this.frame5, 5, this.frame6, 7, this.frame8, 11, this.frame12, 13, this.frame14, 19, this.frame20);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            if (SSF2API.isReady() && this.self)
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
                this.self.updateAuraDamage([1, 2]);
                this.self.setXSpeed(this.self.flipX(14));
                this.self.updateAuraPaws();
            };
        }

        internal function frame2():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame3():*
        {
            this.self.attachEffect("global_dust_heavy", {
                "scaleX":0.75,
                "scaleY":0.5
            });
            this.self.addEffectToList(this.self.attachEffect("trail_lucario_dash", {
                "scaleX":1.15,
                "scaleY":1.15,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
        }

        internal function frame4():*
        {
            this.self.setXSpeed(this.self.flipX(23));
            this.self.updateAttackStats({"xSpeedDecay":0.88});
            this.self.playAttackSound(1);
            this.self.updateAuraPaws();
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

        internal function frame5():*
        {
            this.self.setXSpeed(this.self.flipX(18));
        }

        internal function frame6():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":(6 * this.self.auraMultiplier),
                "power":56,
                "kbConstant":50,
                "effectSound":"lucario_hit_s"
            });
            this.self.updateAttackBoxStats(2, {
                "damage":(6 * this.self.auraMultiplier),
                "power":56,
                "kbConstant":50,
                "effectSound":"lucario_hit_s"
            });
        }

        internal function frame8():*
        {
            this.self.updateAttackStats({"air_ease":-1});
        }

        internal function frame12():*
        {
            if (this.self.isOnGround())
            {
                this.self.setXSpeed((this.self.getXSpeed() * 0.75));
                this.self.updateAttackStats({"xSpeedDecay":-1.1});
                this.self.updateAttackStats({
                    "canFallOff":false,
                    "cancelWhenAirborne":true
                });
            }
            else
            {
                this.self.updateAttackStats({
                    "allowDoubleJump":true,
                    "doubleJumpCancelAttack":true
                });
            };
        }

        internal function frame14():*
        {
            if (this.self.isOnGround())
            {
                this.self.setXSpeed((this.self.getXSpeed() * 0.5));
            };
            this.self.updateAuraPaws();
        }

        internal function frame20():*
        {
            this.self.endAttack();
        }


    }
}

