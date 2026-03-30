package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class fox_combo_36 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var attackBox3:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;
        public var controls:Object;
        public var used:Boolean;
        public var used2:Boolean;
        public var time:Number;
        public var pressed1:Boolean;
        public var pressed2:Boolean;

        public function fox_combo_36()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 5, this.frame6, 7, this.frame8, 8, this.frame9, 9, this.frame10, 10, this.frame11, 11, this.frame12, 15, this.frame16, 16, this.frame17, 17, this.frame18, 19, this.frame20, 22, this.frame23, 23, this.frame24, 26, this.frame27, 27, this.frame28, 30, this.frame31, 31, this.frame32, 34, this.frame35, 39, this.frame40, 40, this.frame41);
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

        public function checkForGoToJab3():*
        {
            if (this.pressed2)
            {
                this.pressed1 = false;
                this.pressed2 = false;
                this.self.stancePlayFrame("hit3");
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.controls = this.self.getControls();
                this.used = this.self.getGlobalVariable("jab");
                this.used2 = this.self.getGlobalVariable("jab2");
                this.time = (SSF2API.getElapsedFrames() - this.self.getGlobalVariable("lastUsedJab") || -999);
                if (this.used && (this.time <= 12))
                {
                    this.self.stancePlayFrame("hit2");
                }
                else if (this.used2 && (this.time <= 10))
                {
                    this.self.stancePlayFrame("hit3");
                };
            };
            this.pressed1 = false;
            this.pressed2 = false;
        }

        internal function frame3():*
        {
            this.self.setGlobalVariable("jab", true);
            this.self.setGlobalVariable("jab2", false);
            this.pressed1 = false;
            this.checkControls();
        }

        internal function frame4():*
        {
            this.self.attachEffect("global_dust_blast", {
                "x":this.self.flipX(45),
                "y":-28,
                "parentLock":true
            });
            this.self.createTimer(1, 4, this.checkControls);
            this.self.playAttackSound(1);
        }

        internal function frame6():*
        {
            this.self.createTimer(1, 2, this.checkForGoToJab2);
        }

        internal function frame8():*
        {
            this.self.endAttack();
        }

        internal function frame9():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":4,
                "direction":85,
                "hitStun":3,
                "effectSound":"brawl_punch_m"
            });
            this.self.refreshAttackID();
            this.self.setGlobalVariable("jab", false);
            this.self.setGlobalVariable("jab2", true);
            this.self.setGlobalVariable("lastUsedJab", SSF2API.getElapsedFrames());
            this.self.destroyTimer(this.checkControls);
            this.self.destroyTimer(this.checkForGoToJab2);
        }

        internal function frame10():*
        {
            this.self.attachEffect("global_dust_blast", {
                "x":this.self.flipX(45),
                "y":-20,
                "parentLock":true
            });
            this.pressed1 = false;
            this.checkControls();
            this.self.playAttackSound(1);
        }

        internal function frame11():*
        {
            this.self.createTimer(1, 5, this.checkControls);
        }

        internal function frame12():*
        {
            this.self.createTimer(1, 4, this.checkForGoToJab3);
        }

        internal function frame16():*
        {
            this.self.endAttack();
        }

        internal function frame17():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":1,
                "direction":45,
                "power":50,
                "hitStun":5,
                "effectSound":"brawl_kick_s"
            });
            this.self.updateAttackBoxStats(2, {
                "damage":1,
                "direction":45,
                "power":50,
                "hitStun":5,
                "effectSound":"brawl_kick_s"
            });
            this.self.updateAttackBoxStats(3, {
                "damage":1,
                "direction":45,
                "power":50,
                "hitStun":5,
                "effectSound":"brawl_kick_s"
            });
            this.self.setGlobalVariable("jab", false);
            this.self.setGlobalVariable("jab2", false);
            this.self.setGlobalVariable("lastUsedJab", SSF2API.getElapsedFrames());
            this.self.destroyTimer(this.checkControls);
            this.self.destroyTimer(this.checkForGoToJab3);
            this.pressed1 = false;
            this.self.createTimer(1, -1, this.checkControls);
            this.self.playVoiceSound(1);
        }

        internal function frame18():*
        {
            this.self.refreshAttackID();
        }

        internal function frame20():*
        {
            this.self.playAttackSound(2);
            this.self.attachEffect("global_dust_light");
        }

        internal function frame23():*
        {
            this.self.refreshAttackID();
        }

        internal function frame24():*
        {
            this.self.playAttackSound(3);
            this.self.attachEffect("global_dust_light");
        }

        internal function frame27():*
        {
            this.self.refreshAttackID();
        }

        internal function frame28():*
        {
            this.self.playAttackSound(2);
            this.self.attachEffect("global_dust_light");
        }

        internal function frame31():*
        {
            this.self.refreshAttackID();
        }

        internal function frame32():*
        {
            this.self.playAttackSound(3);
            this.self.attachEffect("global_dust_light");
        }

        internal function frame35():*
        {
            if (this.pressed2 || this.controls.BUTTON2)
            {
                this.pressed1 = false;
                this.pressed2 = false;
                this.self.stancePlayFrame("again");
            };
        }

        internal function frame40():*
        {
            this.self.endAttack();
        }

        internal function frame41():*
        {
        }


    }
}

