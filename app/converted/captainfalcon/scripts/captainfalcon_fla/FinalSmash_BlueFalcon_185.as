package captainfalcon_fla
{
    import flash.display.MovieClip;

    public dynamic class FinalSmash_BlueFalcon_185 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var grabBox:MovieClip;
        public var touchBox:MovieClip;
        public var continuePlaying:Boolean;
        public var self:CaptainExt;
        public var fs_ground:Boolean;
        public var opponents:Array;
        public var i:int;
        public var foe:*;

        public function FinalSmash_BlueFalcon_185()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 10, this.frame11, 12, this.frame13, 16, this.frame17, 31, this.frame32, 60, this.frame61, 203, this.frame204, 237, this.frame238, 238, this.frame239, 285, this.frame286, 286, this.frame287, 310, this.frame311, 311, this.frame312, 312, this.frame313, 314, this.frame315, 322, this.frame323, 324, this.frame325, 328, this.frame329, 343, this.frame344, 373, this.frame374, 549, this.frame550, 550, this.frame551, 553, this.frame554, 578, this.frame579, 579, this.frame580, 603, this.frame604, 604, this.frame605);
        }

        public function damageAllGrabbedOpponents():void
        {
            var _local_1:Array = this.self.getGrabbedOpponents();
            for (var _local_2:int = 0; _local_2 < _local_1.length; _local_2++)
            {
                if (_local_1[_local_2] && !(_local_1[_local_2].isDisposed()))
                {
                    _local_1[_local_2].takeDamage({
                        "damage":5,
                        "priority":7,
                        "hitStun":5,
                        "hitLag":-1,
                        "direction":60,
                        "power":55,
                        "kbConstant":100,
                        "bypassNonGrabbed":true,
                        "hasEffect":true,
                        "effectSound":"brawl_punch_l"
                    }, this.self);
                };
            };
        }

        public function checkGrabbed():Boolean
        {
            var _local_1:* = this.self.getGrabbedOpponents()[0];
            if (_local_1 == null)
            {
                return false;
            };
            return true;
        }

        public function hitEffect():void
        {
            var _local_1:* = this.self.getGrabbedOpponents()[0];
            _local_1.forceHitStun(2);
            this.self.forceHitStun(2);
            _local_1.setDamage(((_local_1.getGameObjectStat("stamina") > 0) ? (_local_1.getDamage() - 5) : (_local_1.getDamage() + 5)));
            _local_1.attachEffect("effect_heavyHit", {
                "scaleX":0.8,
                "scaleY":0.9
            });
            _local_1.throbDamageCounter();
            this.self.destroyTimer(this.hitEffect);
        }

        internal function frame1():*
        {
            this.continuePlaying = false;
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as CaptainExt);
                this.self.camFocus(20);
                this.fs_ground = this.self.isOnGround();
                if (!this.fs_ground)
                {
                    gotoAndStop("fs_air");
                };
            };
        }

        internal function frame3():*
        {
            this.self.playVoiceSound(1);
        }

        internal function frame11():*
        {
            this.self.playSound("fs_fingersnap");
        }

        internal function frame13():*
        {
            this.self.playSound("entranceLeave");
            this.self.playSound("brawl_punch_l");
            this.self.createTimer(1, 0, this.hitEffect, {"condition":this.checkGrabbed});
        }

        internal function frame17():*
        {
            if (!(this.self.getGrabbedOpponents()[0]))
            {
                this.self.stancePlayFrame("fail");
            };
        }

        internal function frame32():*
        {
            this.self.triggerFSCutscene();
        }

        internal function frame61():*
        {
            this.self.forceGrabbedHurtFrame("downed");
        }

        internal function frame204():*
        {
            this.self.forceGrabbedHurtFrame("hurt1");
        }

        internal function frame238():*
        {
            this.self.playSound("entranceLeave");
            this.self.playSound("brawl_punch_l");
        }

        internal function frame239():*
        {
            this.self.destroyTimer(this.hitEffect);
            this.damageAllGrabbedOpponents();
        }

        internal function frame286():*
        {
            this.self.forceOnGround(5);
            if (!this.self.isOnGround())
            {
                this.self.updateAttackStats({"allowControl":true});
                this.self.resetJumps();
                this.self.toJump();
            };
        }

        internal function frame287():*
        {
            this.self.endAttack();
        }

        internal function frame311():*
        {
            this.self.forceOnGround(5);
            if (!this.self.isOnGround())
            {
                this.self.updateAttackStats({"allowControl":true});
                this.self.resetJumps();
                this.self.toJump();
            };
        }

        internal function frame312():*
        {
            this.self.endAttack();
        }

        internal function frame313():*
        {
            if (SSF2API.isReady())
            {
                this.self.camFocus(20);
            };
            this.opponents = this.self.getGrabbedOpponents();
            this.i = 0;
            while (this.i < this.opponents.length)
            {
                if (this.opponents[this.i] && !(this.opponents[this.i].isDisposed()))
                {
                    this.opponents[this.i].takeDamage({
                        "damage":5,
                        "priority":7,
                        "hitStun":5,
                        "hitLag":-1,
                        "direction":60,
                        "power":55,
                        "kbConstant":100,
                        "bypassNonGrabbed":true,
                        "hasEffect":true,
                        "effectSound":"brawl_punch_l"
                    }, this.self);
                };
                this.i++;
            };
        }

        internal function frame315():*
        {
            this.self.playVoiceSound(1);
        }

        internal function frame323():*
        {
            this.self.playSound("fs_fingersnap");
        }

        internal function frame325():*
        {
            this.self.playSound("entranceLeave");
            this.self.playSound("brawl_punch_l");
            this.self.createTimer(1, 0, this.hitEffect, {"condition":this.checkGrabbed});
            this.foe = this.self.getGrabbedOpponents()[0];
            if (this.foe == null)
            {
                return false;
            };
            return true;
        }

        internal function frame329():*
        {
            if (!(this.self.getGrabbedOpponents()[0]))
            {
                this.self.stancePlayFrame("fail_air");
            };
        }

        internal function frame344():*
        {
            this.self.triggerFSCutscene();
        }

        internal function frame374():*
        {
            this.self.forceGrabbedHurtFrame("downed");
        }

        internal function frame550():*
        {
            this.self.playSound("entranceLeave");
            this.self.playSound("brawl_punch_l");
        }

        internal function frame551():*
        {
            this.self.destroyTimer(this.hitEffect);
            this.damageAllGrabbedOpponents();
        }

        internal function frame554():*
        {
            this.damageAllGrabbedOpponents();
        }

        internal function frame579():*
        {
            this.self.forceOnGround(5);
            if (!this.self.isOnGround())
            {
                this.self.updateAttackStats({"allowControl":true});
                this.self.resetJumps();
                this.self.toJump();
            };
        }

        internal function frame580():*
        {
            this.self.endAttack();
        }

        internal function frame604():*
        {
            this.self.forceOnGround(5);
            if (!this.self.isOnGround())
            {
                this.self.updateAttackStats({"allowControl":true});
                this.self.resetJumps();
                this.self.toJump();
            };
        }

        internal function frame605():*
        {
            this.self.endAttack();
        }


    }
}

