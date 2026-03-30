package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class SideSpecialGround_55 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var gordo:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:DededeExt;
        public var gordoReady:Boolean;
        public var curFrame:int;
        public var atkID:*;
        public var atkilled:Boolean;

        public function SideSpecialGround_55()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 4, this.frame5, 5, this.frame6, 6, this.frame7, 7, this.frame8, 8, this.frame9, 9, this.frame10, 10, this.frame11, 11, this.frame12, 12, this.frame13, 13, this.frame14, 14, this.frame15, 15, this.frame16, 30, this.frame31);
        }

        public function killAttackboxes():void
        {
            SSF2API.print("ha ha you dorks failed.");
            this.self.updateAttackBoxStats(1, {
                "damage":0,
                "power":0,
                "kbConstant":0,
                "hasEffect":false
            });
            this.atkilled = true;
        }

        public function checkAtkilled():void
        {
            if (this.atkilled)
            {
                this.self.updateAttackStats({"atk_id":this.atkID});
                this.self.updateAttackBoxStats(1, {
                    "atk_id":this.atkID,
                    "damage":9,
                    "power":90,
                    "kbConstant":30,
                    "hasEffect":true
                });
                this.atkilled = false;
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
            this.gordoReady = false;
            if (SSF2API.isReady() && this.self)
            {
                this.curFrame = this.self.getGlobalVariable("DaymanSSpecFrame");
                this.self.setGlobalVariable("DaymanSSpecFrame", 0);
                this.gordoReady = this.self.getGlobalVariable("DaymanSSpecReady");
                this.self.setGlobalVariable("DaymanSSpecReady", false);
                this.atkID = this.self.getGlobalVariable("DaymanSSpecAtkID");
                this.self.setGlobalVariable("DaymanSSpecAtkID", null);
                this.atkilled = false;
                if (this.curFrame > 1)
                {
                    this.self.stancePlayFrame(this.curFrame);
                }
                else if ((this.self.gordo == null) || this.self.gordo.isDisposed())
                {
                    this.gordoReady = true;
                };
            };
        }

        internal function frame3():*
        {
            if (!this.gordoReady)
            {
                this.gordo.visible = false;
            };
        }

        internal function frame4():*
        {
            if (!this.gordoReady)
            {
                this.gordo.visible = false;
            };
        }

        internal function frame5():*
        {
            if (!this.gordoReady)
            {
                this.gordo.visible = false;
            };
        }

        internal function frame6():*
        {
            if (!this.gordoReady)
            {
                this.gordo.visible = false;
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_dedede_fspec_spawn");
            };
        }

        internal function frame7():*
        {
            if (!this.gordoReady)
            {
                this.gordo.visible = false;
            };
        }

        internal function frame8():*
        {
            if (!this.gordoReady)
            {
                this.gordo.visible = false;
            };
            this.self.attachEffect("global_dust_heavy");
        }

        internal function frame9():*
        {
            if (!this.gordoReady)
            {
                this.gordo.visible = false;
            };
        }

        internal function frame10():*
        {
            if (!this.gordoReady)
            {
                this.gordo.visible = false;
            };
        }

        internal function frame11():*
        {
            if (!this.gordoReady)
            {
                this.gordo.visible = false;
            };
        }

        internal function frame12():*
        {
            if (!this.gordoReady)
            {
                this.gordo.visible = false;
            };
        }

        internal function frame13():*
        {
            if (!this.gordoReady)
            {
                this.gordo.visible = false;
            };
        }

        internal function frame14():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                if (this.gordoReady)
                {
                    this.self.playSound("ssf2_snd_sfx_dedede_fspec_launch");
                }
                else
                {
                    this.self.playSound("ssf2_snd_sfx_dedede_swing_m");
                };
                this.self.attachEffect("global_dust_heavy", {
                    "x":this.self.flipX(-10),
                    "y":3,
                    "scaleX":-0.5,
                    "scaleY":-0.5
                });
            };
            if (!this.gordoReady)
            {
                this.gordo.visible = false;
            };
        }

        internal function frame15():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.checkAtkilled();
            };
            if (!this.gordoReady)
            {
                this.gordo.visible = false;
            };
        }

        internal function frame16():*
        {
            if ((this.curFrame != currentFrame) && this.gordoReady)
            {
                this.self.gordo = this.self.fireProjectile("dedede_gordo", 0, -25);
                this.self.gordo.safeMove(this.self.flipX(60), 0);
            };
        }

        internal function frame31():*
        {
            this.self.endAttack();
        }


    }
}

