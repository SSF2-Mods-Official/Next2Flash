package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class Jab_29 extends MovieClip
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
        public var pressed:Boolean;
        public var repressed:Boolean;
        public var jab:Number;
        public var playsound:Number;
        public var audio:Number;

        public function Jab_29()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 4, this.frame5, 7, this.frame8, 11, this.frame12, 15, this.frame16, 16, this.frame17, 17, this.frame18, 21, this.frame22, 24, this.frame25, 28, this.frame29, 29, this.frame30, 30, this.frame31, 32, this.frame33, 33, this.frame34, 44, this.frame45, 46, this.frame47, 48, this.frame49);
        }

        public function checkControls(_arg_1:*=null):*
        {
            if (!this.self.getControls().BUTTON2)
            {
                this.pressed = false;
            }
            else if (this.self.getControls().BUTTON2 && !(this.pressed))
            {
                this.repressed = true;
                this.pressed = true;
            };
        }

        public function jabCheck(_arg_1:*=null):*
        {
            if ((this.jab == 1) && this.repressed && this.self.getControls().BUTTON2)
            {
                this.self.stancePlayFrame("jab2");
                this.self.destroyTimer(this.jabCheck);
            }
            else if ((this.jab == 2) && this.repressed && this.self.getControls().BUTTON2)
            {
                this.self.stancePlayFrame("jab3");
                this.self.destroyTimer(this.jabCheck);
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            this.pressed = true;
            this.repressed = false;
            this.jab = 1;
            if (SSF2API.isReady() && this.self)
            {
                this.playsound = SSF2API.random();
                this.audio = this.self.getGlobalVariable("audio");
                this.self.createTimer(1, -1, this.checkControls);
                this.self.updateAuraDamage([1, 2]);
                this.self.updateAuraPaws();
            };
        }

        internal function frame3():*
        {
            this.self.playAttackSound(1);
            this.self.updateAuraPaws();
        }

        internal function frame5():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame8():*
        {
            this.self.createTimer(1, -1, this.jabCheck);
        }

        internal function frame12():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame16():*
        {
            this.self.endAttack();
        }

        internal function frame17():*
        {
            this.repressed = false;
            this.jab = 2;
            this.self.updateAttackBoxStats(1, {
                "direction":50,
                "kbConstant":18,
                "power":55,
                "hitLag":-1.2
            });
            this.self.updateAttackBoxStats(2, {
                "direction":70,
                "kbConstant":18,
                "power":35,
                "hitLag":-1.2
            });
            this.self.refreshAttackID();
        }

        internal function frame18():*
        {
            this.self.playAttackSound(2);
            this.self.setXSpeed(5, false);
            this.self.addEffectToList(this.self.attachEffect("trail_lucario_jab2", {
                "scaleX":1.15,
                "scaleY":1.15,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.clearEffectsOnStateChange();
            this.self.updateAuraPaws();
        }

        internal function frame22():*
        {
            this.self.createTimer(1, -1, this.jabCheck);
        }

        internal function frame25():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame29():*
        {
            this.self.endAttack();
        }

        internal function frame30():*
        {
            this.self.updateAttackBoxStats(1, {
                "effectSound":"lucario_hit_m",
                "damage":(4 * this.self.auraMultiplier),
                "power":48,
                "kbConstant":90,
                "direction":50,
                "hitLag":-1,
                "aura":false,
                "stackKnockback":true
            });
            this.self.updateAttackBoxStats(2, {
                "effectSound":"lucario_hit_m",
                "damage":(4 * this.self.auraMultiplier),
                "power":48,
                "kbConstant":90,
                "direction":50,
                "hitLag":-1,
                "aura":false,
                "stackKnockback":true
            });
            this.self.refreshAttackID();
            this.self.updateAuraPaws();
        }

        internal function frame31():*
        {
            this.self.setXSpeed(6, false);
            this.self.updateAuraPaws();
        }

        internal function frame33():*
        {
            this.self.playAttackSound(3);
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

        internal function frame34():*
        {
            this.self.addEffectToList(this.self.attachEffect("trail_lucario_jab3", {
                "scaleX":1.15,
                "scaleY":1.15,
                "parentLock":true,
                "syncHitStun":true
            }));
            this.self.updateAuraPaws();
        }

        internal function frame45():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_m1");
            }
            else
            {
                this.self.playSound("lucario_step1");
            };
        }

        internal function frame47():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame49():*
        {
            this.self.endAttack();
        }


    }
}

