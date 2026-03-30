package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class GokuKirby_238 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var aurabase:MovieClip;
        public var hitBox:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var atkilled:Boolean;
        public var controls:*;
        public var curFrame:int;
        public var curCharge:int;
        public var isControlCheck:Boolean;
        public var flip:Boolean;

        public function GokuKirby_238()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 7, this.frame8, 13, this.frame14, 22, this.frame23, 41, this.frame42, 56, this.frame57, 75, this.frame76, 90, this.frame91, 127, this.frame128, 132, this.frame133, 137, this.frame138, 142, this.frame143, 149, this.frame150, 155, this.frame156, 156, this.frame157, 157, this.frame158, 158, this.frame159, 159, this.frame160, 160, this.frame161, 161, this.frame162, 162, this.frame163, 163, this.frame164, 164, this.frame165, 165, this.frame166, 179, this.frame180, 180, this.frame181, 181, this.frame182, 182, this.frame183, 183, this.frame184, 184, this.frame185, 185, this.frame186, 186, this.frame187, 187, this.frame188, 203, this.frame204, 204, this.frame205, 205, this.frame206, 206, this.frame207, 207, this.frame208, 208, this.frame209, 209, this.frame210, 210, this.frame211, 211, this.frame212, 231, this.frame232, 232, this.frame233, 233, this.frame234, 234, this.frame235, 235, this.frame236, 236, this.frame237, 237, this.frame238, 238, this.frame239, 239, this.frame240, 240, this.frame241, 241, this.frame242, 267, this.frame268, 271, this.frame272, 272, this.frame273, 278, this.frame279, 279, this.frame280, 280, this.frame281, 281, this.frame282, 282, this.frame283, 283, this.frame284, 284, this.frame285, 285, this.frame286, 297, this.frame298);
        }

        public function checkControls():void
        {
            this.controls = this.self.getControls();
            if (!this.controls.BUTTON1)
            {
                this.self.destroyTimer(this.checkControls);
                if (this.curCharge >= 4)
                {
                    this.self.stancePlayFrame("attack2");
                }
                else if (this.curCharge > 0)
                {
                    this.self.stancePlayFrame("attack");
                }
                else
                {
                    this.self.stancePlayFrame("quick");
                };
            };
        }

        public function effects():void
        {
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(5),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        public function killAttackboxes():void
        {
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
                this.self.updateAttackBoxStats(1, {
                    "damage":2,
                    "power":35,
                    "kbConstant":49,
                    "hasEffect":true
                });
                this.atkilled = false;
            };
        }

        public function disableNeutralB():void
        {
            this.self.setAttackEnabled(false, "b");
            this.self.setAttackEnabled(false, "b_air");
            this.self.createTimer(15, 1, this.enableNeutralB, {"persistent":true});
        }

        public function enableNeutralB():void
        {
            this.self.setAttackEnabled(true, "b");
            this.self.setAttackEnabled(true, "b_air");
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.atkilled = false;
            if (SSF2API.isReady() && this.self)
            {
                this.controls = this.self.getControls();
                this.curFrame = this.self.getGlobalVariable("GokuKirbyNSpecFrame");
                this.curCharge = this.self.getGlobalVariable("GokuKirbyNSpecCharge");
                this.isControlCheck = this.self.getGlobalVariable("GokuKirbyNSpecControl");
                this.flip = this.self.getGlobalVariable("GokuKirbyNSpecFlip");
                this.self.setGlobalVariable("GokuKirbyNSpecFrame", 0);
                this.self.setGlobalVariable("GokuKirbyNSpecCharge", 0);
                this.self.setGlobalVariable("GokuKirbyNSpecControl", false);
                this.self.setGlobalVariable("GokuKirbyNSpecFlip", false);
                if (this.curFrame > 1)
                {
                    if (this.isControlCheck)
                    {
                        this.self.createTimer(1, -1, this.checkControls);
                    };
                    this.self.stancePlayFrame(this.curFrame);
                }
                else
                {
                    this.self.createTimer(1, -1, this.checkControls);
                };
            };
        }

        internal function frame5():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.destroyTimer(this.checkControls);
            };
        }

        internal function frame8():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.playVoiceSound(1);
            };
            this.curCharge = 1;
            this.self.createTimer(4, -1, this.effects);
        }

        internal function frame14():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.playAttackSound(1);
            };
        }

        internal function frame23():*
        {
            if (this.curFrame != currentFrame)
            {
                this.controls = this.self.getControls();
                if (this.controls.BUTTON1)
                {
                }
                else
                {
                    this.self.createTimer(1, -1, this.checkControls);
                };
            };
        }

        internal function frame42():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.destroyTimer(this.checkControls);
                this.self.playVoiceSound(2);
                this.self.playAttackSound(1);
            };
            this.curCharge = 2;
        }

        internal function frame57():*
        {
            if (this.curFrame != currentFrame)
            {
                this.controls = this.self.getControls();
                if (this.controls.BUTTON1)
                {
                }
                else
                {
                    this.self.createTimer(1, -1, this.checkControls);
                };
            };
        }

        internal function frame76():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.destroyTimer(this.checkControls);
                this.self.playVoiceSound(3);
                this.self.playAttackSound(1);
            };
            this.curCharge = 3;
        }

        internal function frame91():*
        {
            if (this.curFrame != currentFrame)
            {
                this.controls = this.self.getControls();
                if (this.controls.BUTTON1)
                {
                }
                else
                {
                    this.self.createTimer(1, -1, this.checkControls);
                };
            };
        }

        internal function frame128():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.destroyTimer(this.checkControls);
                this.self.playVoiceSound(4);
                this.self.playAttackSound(1);
                this.self.playSound("ki_charge_start");
                this.self.playSound("ki_charge_loop");
                SSF2API.getCamera().shake(4);
            };
            this.curCharge = 4;
        }

        internal function frame133():*
        {
            this.self.playSound("ki_charge_loop");
        }

        internal function frame138():*
        {
            this.self.playSound("ki_charge_loop");
        }

        internal function frame143():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.createTimer(1, -1, this.checkControls);
            };
        }

        internal function frame150():*
        {
            this.self.playSound("ki_charge_loop");
        }

        internal function frame156():*
        {
            this.self.stancePlayFrame("loop");
        }

        internal function frame157():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.updateAttackStats({"air_ease":0});
                this.flip = false;
                this.controls = this.self.getControls();
                if ((this.controls.LEFT != this.controls.RIGHT) && (this.controls.RIGHT != this.self.isFacingRight()))
                {
                    this.flip = true;
                };
            };
        }

        internal function frame158():*
        {
            if (this.curFrame != currentFrame)
            {
                this.controls = this.self.getControls();
                if ((this.controls.LEFT != this.controls.RIGHT) && (this.controls.RIGHT != this.self.isFacingRight()))
                {
                    this.flip = true;
                };
                if (this.flip)
                {
                    this.self.flip();
                };
            };
        }

        internal function frame159():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.destroyTimer(this.effects);
                this.self.attachEffect("global_dust_heavy", {"x":this.self.flipX(-5)});
                if (this.curCharge >= 4)
                {
                    this.self.stancePlayFrame("lv4");
                }
                else if (this.curCharge >= 3)
                {
                    this.self.stancePlayFrame("lv3");
                }
                else if (this.curCharge >= 2)
                {
                    this.self.stancePlayFrame("lv2");
                }
                else
                {
                    this.self.playAttackSound(2);
                    SSF2API.getCamera().shake(7);
                    this.self.playVoiceSound(7);
                };
                if (!this.self.isOnGround())
                {
                    this.self.setXSpeed(-3, false);
                };
            };
        }

        internal function frame160():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.checkAtkilled();
                this.self.refreshAttackID();
            };
        }

        internal function frame161():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.checkAtkilled();
                this.self.refreshAttackID();
            };
        }

        internal function frame162():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.checkAtkilled();
                this.self.refreshAttackID();
            };
        }

        internal function frame163():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.checkAtkilled();
                this.self.refreshAttackID();
            };
        }

        internal function frame164():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.checkAtkilled();
                this.self.refreshAttackID();
            };
        }

        internal function frame165():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.checkAtkilled();
                this.self.refreshAttackID();
            };
        }

        internal function frame166():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.self.updateAttackBoxStats(1, {
                    "damage":7,
                    "power":50,
                    "kbConstant":95,
                    "hasEffect":true
                });
                this.self.refreshAttackID();
            };
        }

        internal function frame180():*
        {
            this.disableNeutralB();
            this.self.endAttack();
        }

        internal function frame181():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.playVoiceSound(7);
                this.self.playAttackSound(2);
                SSF2API.getCamera().shake(7);
                if (!this.self.isOnGround())
                {
                    this.self.setXSpeed(-5, false);
                };
            };
        }

        internal function frame182():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.checkAtkilled();
                this.self.refreshAttackID();
            };
        }

        internal function frame183():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.checkAtkilled();
                this.self.refreshAttackID();
            };
        }

        internal function frame184():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.checkAtkilled();
                this.self.refreshAttackID();
            };
        }

        internal function frame185():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.checkAtkilled();
                this.self.refreshAttackID();
            };
        }

        internal function frame186():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.checkAtkilled();
                this.self.refreshAttackID();
            };
        }

        internal function frame187():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.checkAtkilled();
                this.self.refreshAttackID();
            };
        }

        internal function frame188():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.self.updateAttackBoxStats(1, {
                    "damage":10,
                    "power":55,
                    "kbConstant":95,
                    "hasEffect":true
                });
                this.self.refreshAttackID();
            };
        }

        internal function frame204():*
        {
            this.disableNeutralB();
            this.self.endAttack();
        }

        internal function frame205():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.playVoiceSound(7);
                this.self.playAttackSound(2);
                SSF2API.getCamera().shake(7);
                if (!this.self.isOnGround())
                {
                    this.self.setXSpeed(-7, false);
                };
            };
        }

        internal function frame206():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.checkAtkilled();
                this.self.refreshAttackID();
            };
        }

        internal function frame207():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.checkAtkilled();
                this.self.refreshAttackID();
            };
        }

        internal function frame208():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.checkAtkilled();
                this.self.refreshAttackID();
            };
        }

        internal function frame209():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.checkAtkilled();
                this.self.refreshAttackID();
            };
        }

        internal function frame210():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.checkAtkilled();
                this.self.refreshAttackID();
            };
        }

        internal function frame211():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.checkAtkilled();
                this.self.refreshAttackID();
            };
        }

        internal function frame212():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.self.updateAttackBoxStats(1, {
                    "damage":15,
                    "power":65,
                    "kbConstant":95,
                    "hasEffect":true,
                    "effect_id":"effect_magichit_heavy",
                    "effectSound":"brawl_magic_l"
                });
                this.self.refreshAttackID();
            };
        }

        internal function frame232():*
        {
            this.disableNeutralB();
            this.self.endAttack();
        }

        internal function frame233():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.updateAttackStats({"air_ease":0});
                this.flip = false;
                this.controls = this.self.getControls();
                if ((this.controls.LEFT != this.controls.RIGHT) && (this.controls.RIGHT != this.self.isFacingRight()))
                {
                    this.flip = true;
                };
            };
        }

        internal function frame234():*
        {
            if (this.curFrame != currentFrame)
            {
                this.controls = this.self.getControls();
                if ((this.controls.LEFT != this.controls.RIGHT) && (this.controls.RIGHT != this.self.isFacingRight()))
                {
                    this.flip = true;
                };
                if (this.flip)
                {
                    this.self.flip();
                };
            };
        }

        internal function frame235():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.playVoiceSound(5);
                this.self.playAttackSound(2);
                SSF2API.getCamera().shake(7);
                if (!this.self.isOnGround())
                {
                    this.self.setXSpeed(-9, false);
                };
            };
        }

        internal function frame236():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.checkAtkilled();
                this.self.refreshAttackID();
            };
        }

        internal function frame237():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.checkAtkilled();
                this.self.refreshAttackID();
            };
        }

        internal function frame238():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.checkAtkilled();
                this.self.refreshAttackID();
            };
        }

        internal function frame239():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.checkAtkilled();
                this.self.refreshAttackID();
            };
        }

        internal function frame240():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.checkAtkilled();
                this.self.refreshAttackID();
            };
        }

        internal function frame241():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.checkAtkilled();
                this.self.refreshAttackID();
            };
        }

        internal function frame242():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.self.updateAttackBoxStats(1, {
                    "damage":24,
                    "direction":55,
                    "power":80,
                    "kbConstant":100,
                    "hasEffect":true,
                    "effect_id":"effect_magichit_heavy",
                    "effectSound":"brawl_magic_l"
                });
                this.self.refreshAttackID();
            };
        }

        internal function frame268():*
        {
            this.disableNeutralB();
            this.self.endAttack();
        }

        internal function frame272():*
        {
            this.self.createTimer(4, -1, this.effects);
        }

        internal function frame273():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.playAttackSound(1);
            };
        }

        internal function frame279():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.playVoiceSound(7);
            };
        }

        internal function frame280():*
        {
            this.self.updateAttackStats({"air_ease":0});
        }

        internal function frame281():*
        {
            if (this.curFrame != currentFrame)
            {
                this.self.destroyTimer(this.effects);
                if (!this.self.isOnGround())
                {
                    this.self.setXSpeed(-3, false);
                };
            };
            this.self.attachEffect("global_dust_heavy", {"x":this.self.flipX(-5)});
        }

        internal function frame282():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.self.playAttackSound(2);
                SSF2API.getCamera().shake(7);
            };
        }

        internal function frame283():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.checkAtkilled();
                this.self.refreshAttackID();
            };
        }

        internal function frame284():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.checkAtkilled();
                this.self.refreshAttackID();
            };
        }

        internal function frame285():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.checkAtkilled();
                this.self.refreshAttackID();
            };
        }

        internal function frame286():*
        {
            if (this.curFrame == currentFrame)
            {
                this.killAttackboxes();
            }
            else
            {
                this.self.updateAttackBoxStats(1, {
                    "damage":4,
                    "hitStun":2,
                    "power":50,
                    "kbConstant":95,
                    "hasEffect":true,
                    "effectSound":"brawl_magic_m"
                });
                this.self.refreshAttackID();
            };
        }

        internal function frame298():*
        {
            this.disableNeutralB();
            this.self.endAttack();
        }


    }
}

