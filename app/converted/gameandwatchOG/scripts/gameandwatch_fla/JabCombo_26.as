package gameandwatch_fla
{
    import flash.display.MovieClip;
    import flash.geom.Point;

    public dynamic class JabCombo_26 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:gameandwatchExt;
        public var controls:Object;
        public var pressed1:Boolean;
        public var pressed2:Boolean;
        public var rapidJabStats:Object;
        public var jabFinishStats:Object;

        public function JabCombo_26()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 4, this.frame5, 6, this.frame7, 9, this.frame10, 10, this.frame11, 12, this.frame13, 13, this.frame14, 14, this.frame15, 15, this.frame16, 17, this.frame18, 18, this.frame19, 20, this.frame21, 21, this.frame22, 24, this.frame25, 39, this.frame40);
        }

        public function checkControls():*
        {
            this.controls = this.self.getControls();
            if (!this.controls.BUTTON2)
            {
                this.pressed1 = true;
            };
            if (this.pressed1 && this.controls.BUTTON2)
            {
                this.pressed2 = true;
            };
        }

        public function checkForGoToJab2():*
        {
            if (this.pressed2)
            {
                this.pressed1 = false;
                this.pressed2 = false;
                this.self.stancePlayFrame("hit2");
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as gameandwatchExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.controls = this.self.getControls();
                this.self.createTimer(1, 9, this.checkControls);
            };
            this.pressed1 = false;
            this.pressed2 = false;
        }

        internal function frame3():*
        {
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-10)});
            this.self.playSound("gw_jabpush");
        }

        internal function frame5():*
        {
            this.self.playSound("gw_jabpull");
        }

        internal function frame7():*
        {
            this.self.createTimer(1, 3, this.checkForGoToJab2);
        }

        internal function frame10():*
        {
            this.self.endAttack();
        }

        internal function frame11():*
        {
            this.rapidJabStats = {
                "selfHitStun":0,
                "hitStun":1,
                "weightKB":20,
                "damage":0.5,
                "direction":65,
                "power":0,
                "kbConstant":50
            };
            this.self.updateAttackBoxStats(1, this.rapidJabStats);
            this.self.updateAttackBoxStats(2, this.rapidJabStats);
            this.self.refreshAttackID();
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-10)});
            this.self.destroyTimer(this.checkControls);
            this.self.destroyTimer(this.checkForGoToJab2);
            this.self.createTimer(1, -1, this.checkControls);
            this.self.playSound("gw_jabpush");
        }

        internal function frame13():*
        {
            this.self.playSound("gw_jabpull");
        }

        internal function frame14():*
        {
            this.self.refreshAttackID();
        }

        internal function frame15():*
        {
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-10)});
            this.self.playSound("gw_jabmulti");
        }

        internal function frame16():*
        {
            this.self.refreshAttackID();
            if (this.pressed2 || this.controls.BUTTON2)
            {
                this.pressed1 = false;
                this.pressed2 = false;
            }
            else
            {
                this.self.stancePlayFrame("finish");
            };
        }

        internal function frame18():*
        {
            this.self.attachEffect("global_dust_light", {"x":this.self.flipX(-10)});
            this.self.playSound("gw_jabmulti");
        }

        internal function frame19():*
        {
            if (this.pressed2 || this.controls.BUTTON2)
            {
                this.pressed1 = false;
                this.pressed2 = false;
            }
            else
            {
                this.self.stancePlayFrame("finish");
            };
        }

        internal function frame21():*
        {
            if (this.pressed2 || this.controls.BUTTON2)
            {
                this.self.refreshAttackID();
                this.pressed1 = false;
                this.pressed2 = false;
                this.self.stancePlayFrame("again");
            }
            else
            {
                this.self.stancePlayFrame("finish");
            };
        }

        internal function frame22():*
        {
            if (SSF2API.getPlatformBetweenPoints(new Point((this.self.getX() + this.self.flipX(10)), (this.self.getY() - 2)), new Point((this.self.getX() + this.self.flipX(10)), (this.self.getY() + 15)), {"ignoreFallthrough":false}))
            {
                this.self.safeMove(this.self.flipX(10), 0);
            };
            this.jabFinishStats = {
                "selfHitStun":2,
                "hitStun":4,
                "weightKB":0,
                "damage":3,
                "direction":45,
                "power":55,
                "kbConstant":115,
                "effect_id":"effect_heavyHit",
                "effectSound":"brawl_fire_l",
                "stackKnockback":true
            };
            this.self.updateAttackBoxStats(1, this.jabFinishStats);
            this.self.updateAttackBoxStats(2, this.jabFinishStats);
            this.self.refreshAttackID();
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(5),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
            this.self.playSound("gw_aerial1");
        }

        internal function frame25():*
        {
            this.self.playSound("gw_aerial2");
        }

        internal function frame40():*
        {
            this.self.endAttack();
        }


    }
}

