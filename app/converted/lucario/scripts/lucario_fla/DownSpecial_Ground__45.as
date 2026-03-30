package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class DownSpecial_Ground__45 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;
        public var hit:Boolean;
        public var controls:*;
        public var audio:int;
        public var playSound:Number;
        public var curFrame:int;
        public var back:Boolean;
        public var atkID:*;
        public var atkilled:Boolean;

        public function DownSpecial_Ground__45()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 3, this.frame4, 4, this.frame5, 10, this.frame11, 11, this.frame12, 12, this.frame13, 13, this.frame14, 17, this.frame18, 25, this.frame26, 28, this.frame29, 31, this.frame32);
        }

        public function onHit(_arg_1:*=null):*
        {
            this.hit = true;
        }

        public function killAttackboxes():void
        {
            SSF2API.print("ha ha you dorks failed.");
            this.self.updateAttackBoxStats(1, {
                "damage":0,
                "power":0,
                "kbConstant":0,
                "selfHitStun":0,
                "paralysis":-1,
                "effectSound":null,
                "hasEffect":false
            });
            this.atkilled = true;
        }

        public function soundPlay(_arg_1:int):*
        {
            if (this.audio == _arg_1)
            {
                this.self.setGlobalVariable("audio", 0);
            }
            else
            {
                this.self.playVoiceSound(_arg_1);
                this.self.setGlobalVariable("audio", _arg_1);
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            this.hit = false;
            this.controls = null;
            this.audio = 0;
            this.playSound = 0;
            if (SSF2API.isReady() && this.self)
            {
                this.curFrame = this.self.getGlobalVariable("LucarioDSpecFrame");
                this.self.setGlobalVariable("LucarioDSpecFrame", 0);
                this.back = this.self.getGlobalVariable("LucarioDSpecBack");
                this.self.setGlobalVariable("LucarioDSpecBack", false);
                this.atkID = this.self.getGlobalVariable("LucarioDSpecAtkID");
                this.self.setGlobalVariable("LucarioDSpecAtkID", 0);
                this.atkilled = false;
                this.self.updateAuraDamage([1]);
                this.self.updateAttackBoxStats(1, {"paralysis":(14 + (18 * this.self.auraPercentage))});
                this.self.updateAuraPaws();
                this.self.addEventListener(SSF2Event.ATTACK_HIT, this.onHit);
                if (this.curFrame > 1)
                {
                    if (this.curFrame < 3)
                    {
                    }
                    else if (this.curFrame < 5)
                    {
                        this.self.setInvincibility(true);
                    }
                    else if (this.curFrame < 14)
                    {
                        this.self.setIntangibility(true);
                    }
                    else
                    {
                        this.self.setInvincibility(false);
                        this.self.setIntangibility(false);
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

        internal function frame3():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.setInvincibility(true);
            };
        }

        internal function frame4():*
        {
            if (this.curFrame != currentFrame)
            {
                this.controls = this.self.getControls();
                if (this.controls.RIGHT != this.controls.LEFT)
                {
                    if (this.controls.RIGHT == this.self.isFacingRight())
                    {
                        this.self.setXSpeed(11, false);
                    }
                    else
                    {
                        this.back = true;
                        this.self.setXSpeed(-11, false);
                    };
                };
            };
        }

        internal function frame5():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.setIntangibility(true);
                this.self.setInvincibility(false);
            };
        }

        internal function frame11():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.addEffectToList(this.self.attachEffect("trail_lucario_dspecground", {
                    "scaleX":1.15,
                    "scaleY":1.15,
                    "parentLock":true,
                    "syncHitStun":true
                }));
                this.self.clearEffectsOnStateChange();
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_step_m2");
                }
                else
                {
                    this.self.playSound("lucario_step2");
                };
            };
        }

        internal function frame12():*
        {
            if (this.curFrame != currentFrame)
            {
                this.controls = this.self.getControls();
                if (this.back && (this.controls.RIGHT != this.controls.LEFT) && (this.controls.RIGHT == this.self.isFacingRight()))
                {
                    this.self.setXSpeed(13.2, false);
                };
            };
        }

        internal function frame13():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.self.playAttackSound(2);
                this.self.updateAuraPaws();
                this.audio = this.self.getGlobalVariable("audio");
                this.playSound = SSF2API.random();
                if (this.playSound <= 0.2)
                {
                    this.self.setGlobalVariable("audio", 0);
                }
                else if (this.playSound <= 0.4)
                {
                    this.soundPlay(1);
                }
                else if (this.playSound <= 0.6)
                {
                    this.soundPlay(2);
                }
                else if (this.playSound <= 0.8)
                {
                    this.soundPlay(3);
                }
                else
                {
                    this.soundPlay(4);
                };
            };
            this.self.attachEffect("global_dust_light");
        }

        internal function frame14():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                if (this.atkilled)
                {
                    this.self.updateAttackStats({"atk_id":this.atkID});
                    this.self.updateAttackBoxStats(1, {
                        "atk_id":this.atkID,
                        "damage":8,
                        "power":40,
                        "kbConstant":105,
                        "selfHitStun":7,
                        "paralysis":(14 + (18 * this.self.auraPercentage)),
                        "effectSound":"lucario_hit_dspec",
                        "hasEffect":true
                    });
                    this.self.updateAuraDamage([1]);
                };
                this.self.setIntangibility(false);
            };
        }

        internal function frame18():*
        {
            if (this.hit)
            {
                this.self.stancePlayFrame("skip1");
            };
        }

        internal function frame26():*
        {
            if (this.hit)
            {
                this.self.stancePlayFrame("skip2");
            };
        }

        internal function frame29():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.updateAuraPaws();
            };
        }

        internal function frame32():*
        {
            this.self.endAttack();
        }


    }
}

