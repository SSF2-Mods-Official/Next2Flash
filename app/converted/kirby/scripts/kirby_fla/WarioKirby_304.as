package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class WarioKirby_304 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var grabBox:MovieClip;
        public var hitBox:MovieClip;
        public var touchBox:MovieClip;
        public var self:KirbyExt;
        public var theOpponent:*;
        public var controls2:Object;
        public var formerControl:Object;
        public var controls:Object;
        public var wasPressingAlready:*;
        public var facing:Boolean;
        public var flip:Boolean;
        public var playedOnce:*;
        public var happenedAlready:*;
        public var mashing:*;
        public var waitTimer:*;
        public var endTimer:int;
        public var damageDivide:*;
        public var mashInfluence:*;
        public var chewCount:*;
        public var throwStats:*;
        public var backThrowStats:*;
        public var mouthCloseStats:*;

        public function WarioKirby_304()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 13, this.frame14, 14, this.frame15, 18, this.frame19, 19, this.frame20, 20, this.frame21, 26, this.frame27, 27, this.frame28, 29, this.frame30, 33, this.frame34, 38, this.frame39, 39, this.frame40, 41, this.frame42, 48, this.frame49, 52, this.frame53, 53, this.frame54, 54, this.frame55, 58, this.frame59);
        }

        public function clearTimers():void
        {
            this.self.destroyTimer(this.openMouth);
            this.self.destroyTimer(this.heldControls);
            this.self.destroyTimer(this.getFree);
        }

        public function openMouth():void
        {
            this.controls = this.self.getControls();
            this.waitTimer--;
            if (this.self.getGrabbedOpponents()[0])
            {
                gotoAndStop("grabbed");
                this.self.destroyTimer(this.openMouth);
            }
            else if ((this.waitTimer < 0) || !(this.controls.BUTTON1))
            {
                gotoAndStop("fail");
            };
        }

        public function heldControls():void
        {
            this.controls = this.self.getControls();
            if (!this.wasPressingAlready)
            {
                if (this.controls.BUTTON2 || this.controls.BUTTON1)
                {
                    this.gotoAndStop("chew");
                };
            };
            if ((this.chewCount < 0) || (this.facing && this.controls.RIGHT) || (!(this.facing) && this.controls.LEFT))
            {
                this.gotoAndStop("throw");
            };
            if ((this.facing && this.controls.LEFT) || (!(this.facing) && this.controls.RIGHT))
            {
                this.gotoAndStop("throwback");
            };
            if (!(this.controls.BUTTON1) && !(this.controls.BUTTON2))
            {
                this.wasPressingAlready = false;
            };
        }

        public function getFree():void
        {
            this.endTimer--;
            this.self.destroyTimer(this.getFree);
            if (this.endTimer < 0)
            {
                if (this.mashing)
                {
                    this.self.grabReleaseOpponent();
                    this.self.grabRelease();
                }
                else
                {
                    gotoAndStop("throw");
                };
                return;
            };
            this.mashing = false;
            this.controls2 = this.theOpponent.getControls();
            if (this.controls2.UP && (this.formerControl != "up"))
            {
                this.formerControl = "up";
                this.endTimer -= this.mashInfluence;
                this.mashing = true;
            }
            else if (this.controls2.DOWN && (this.formerControl != "down"))
            {
                this.formerControl = "down";
                this.endTimer -= this.mashInfluence;
                this.mashing = true;
            }
            else if (this.controls2.LEFT && (this.formerControl != "left"))
            {
                this.formerControl = "left";
                this.endTimer -= this.mashInfluence;
                this.mashing = true;
            }
            else if (this.controls2.RIGHT && (this.formerControl != "right"))
            {
                this.formerControl = "right";
                this.endTimer -= this.mashInfluence;
                this.mashing = true;
            }
            else if (this.controls2.BUTTON1 && (this.formerControl != "button1"))
            {
                this.formerControl = "button1";
                this.endTimer -= this.mashInfluence;
                this.mashing = true;
            }
            else if (this.controls2.BUTTON2 && (this.formerControl != "button2"))
            {
                this.formerControl = "button2";
                this.endTimer -= this.mashInfluence;
                this.mashing = true;
            }
            else if (this.controls2.GRAB && (this.formerControl != "grab"))
            {
                this.formerControl = "grab";
                this.endTimer -= this.mashInfluence;
                this.mashing = true;
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.wasPressingAlready = true;
            this.facing = false;
            this.flip = false;
            this.playedOnce = false;
            this.happenedAlready = false;
            this.mashing = false;
            this.waitTimer = 30;
            this.endTimer = 1;
            this.damageDivide = 4;
            this.mashInfluence = 5;
            this.chewCount = 2;
            this.throwStats = {
                "hasEffect":true,
                "damage":6,
                "power":74,
                "kbConstant":31,
                "hitLag":-1.08,
                "hitStun":1,
                "selfHitStun":0,
                "effect_id":null,
                "effectSound":"brawl_kick_l",
                "direction":56
            };
            this.backThrowStats = {
                "hasEffect":true,
                "damage":6,
                "power":74,
                "kbConstant":31,
                "hitLag":-1,
                "hitStun":1,
                "selfHitStun":0,
                "effect_id":null,
                "effectSound":"brawl_kick_l",
                "direction":146
            };
            this.mouthCloseStats = {
                "hasEffect":true,
                "power":70,
                "kbConstant":50,
                "damage":10,
                "weightKB":0,
                "hitLag":-1,
                "hitStun":4,
                "selfHitStun":3,
                "effect_id":"effect_swordSlash",
                "direction":50
            };
            if (this.self && SSF2API.isReady())
            {
                this.controls = this.self.getControls();
                this.facing = this.self.isFacingRight();
            };
        }

        internal function frame3():*
        {
            this.self.playVoiceSound(1);
            this.self.playSound("wario_chomp");
        }

        internal function frame4():*
        {
            this.clearTimers();
            if (this.playedOnce)
            {
                this.self.createTimer(1, 0, this.openMouth);
            };
        }

        internal function frame14():*
        {
            this.playedOnce = true;
            this.gotoAndStop("openWait");
        }

        internal function frame15():*
        {
            this.clearTimers();
            this.self.createTimer(1, 0, this.heldControls);
            this.self.createTimer(1, 0, this.getFree);
            if (!this.happenedAlready)
            {
                this.self.swapDepthsWithGrabbedOpponent(true);
                this.self.updateAttackBoxStats(1, {"bypassNonGrabbed":true});
                this.happenedAlready = true;
                this.theOpponent = this.self.getGrabbedOpponents()[0];
                this.controls2 = this.theOpponent.getControls();
                this.endTimer += (this.theOpponent.getDamage() / this.damageDivide);
                this.self.setXSpeed((this.self.getXSpeed() * 0.6));
            };
        }

        internal function frame19():*
        {
        }

        internal function frame20():*
        {
            gotoAndStop("grabbed");
        }

        internal function frame21():*
        {
            this.clearTimers();
            this.self.createTimer(1, 0, this.getFree);
            this.chewCount--;
            this.self.refreshAttackID();
        }

        internal function frame27():*
        {
            if ((this.chewCount < 0) || (this.endTimer < 0))
            {
                gotoAndStop("throw");
            }
            else
            {
                this.gotoAndStop("grabbed");
            };
            this.controls = this.self.getControls();
            if (this.controls.BUTTON1 || this.controls.BUTTON2)
            {
                this.wasPressingAlready = true;
            };
        }

        internal function frame28():*
        {
            this.clearTimers();
            this.self.updateAttackBoxStats(1, this.throwStats);
            this.self.refreshAttackID();
        }

        internal function frame30():*
        {
            this.self.swapDepthsWithGrabbedOpponent(false);
        }

        internal function frame34():*
        {
            this.self.releaseOpponent();
        }

        internal function frame39():*
        {
            this.self.endAttack();
        }

        internal function frame40():*
        {
            this.clearTimers();
            this.self.updateAttackBoxStats(1, this.backThrowStats);
            this.self.refreshAttackID();
            this.flip = true;
        }

        internal function frame42():*
        {
            this.self.swapDepthsWithGrabbedOpponent(false);
        }

        internal function frame49():*
        {
            this.self.releaseOpponent();
        }

        internal function frame53():*
        {
            this.self.endAttack();
        }

        internal function frame54():*
        {
            this.clearTimers();
            if (this.self.getGrabbedOpponents()[0])
            {
                gotoAndStop("grabbed");
            };
            if (this.flip)
            {
                this.self.flip();
            };
            this.self.updateAttackBoxStats(1, this.mouthCloseStats);
        }

        internal function frame55():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_m");
                SSF2API.getCamera().shake(5);
            }
            else
            {
                this.self.playAttackSound(2);
            };
            this.self.playVoiceSound(2);
        }

        internal function frame59():*
        {
            this.self.endAttack();
        }


    }
}

