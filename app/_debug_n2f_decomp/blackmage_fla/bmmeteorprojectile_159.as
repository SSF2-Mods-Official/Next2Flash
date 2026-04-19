package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class bmmeteorprojectile_159 extends MovieClip {
        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var self:*;
        public var isOnGround:Boolean;
        public var character:*;
        public var temp:*;
        public var dmg:Number;
        public var charge:int;
        public var max:int;
        public function bmmeteorprojectile_159() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(2, frame_3);
            addFrameScript(3, frame_4);
            addFrameScript(4, frame_5);
            addFrameScript(13, frame_14);
            addFrameScript(14, frame_15);
            addFrameScript(27, frame_28);
            addFrameScript(29, frame_30);
            addFrameScript(30, frame_31);
        }
        internal function frame_1():* {
            var attackBox:MovieClip;
            var hitBox:MovieClip;
            var self:*;
            var isOnGround:Boolean;
            var character:*;
            var temp:*;
            var dmg:Number;
            var charge:int;
            var max:int;
            this.self = SSF2API.getProjectile(this);
                        this.isOnGround = false;
                        if (SSF2API.isReady() && this.self)
                        {
                            this.character = this.self.getOwner();
                            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.onGround);
                        };
        }
        internal function frame_3():* {
            this.self.stancePlayFrame("redo");
        }
        internal function frame_4():* {
            this.temp = SSF2API.getProjectile(this);
                        if (!this.self)
                        {
                            this.self = this.temp;
                        };
                        this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.onGround);
                        this.dmg = this.self.getAttackBoxStat(1, "damage");
                        this.charge = this.character.getGlobalVariable("BMageDSpecCharge");
                        this.max = this.character.getAttackStat("chargetime_max");
                        if (this.charge > this.max)
                        {
                            this.charge = this.max;
                        };
                        this.dmg += ((this.charge / this.max) * 23);
                        this.self.updateAttackBoxStats(1, {
                            "damage":this.dmg,
                            "effectSound":"brawl_fire_l"
                        });
                        this.self.addEventListener(SSF2Event.ATTACK_CONNECT, this.toContinue);
                        this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.toContinue);
                        this.self.addEventListener(SSF2Event.ATTACK_HIT_POWER_SHIELD, this.self.flip);
                        this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toContinue);
                        this.self.addEventListener(SSF2Event.HIT_WALL, this.toContinue);
                        this.self.addEventListener(SSF2Event.REVERSE, this.self.flip);
        }
        internal function frame_5():* {
            if (this.isOnGround)
                        {
                            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.toContinue);
                            this.self.removeEventListener(SSF2Event.ATTACK_CONNECT, this.toContinue);
                            this.self.removeEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.toContinue);
                            this.self.removeEventListener(SSF2Event.HIT_WALL, this.toContinue);
                            this.self.removeEventListener(SSF2Event.REVERSE, this.self.flip);
                            this.self.stancePlayFrame("continue");
                        };
        }
        internal function frame_14():* {
            this.self.stancePlayFrame("loop");
        }
        internal function frame_15():* {
            this.self.updateProjectileStats({
                            "maxgravity":0,
                            "canBePocketed":false,
                            "canBeAbsorbed":true
                        });
                        this.self.setXSpeed(0);
                        this.self.setYSpeed(0);
                        this.self.playSound("bombexplode");
        }
        internal function frame_28():* {
            this.self.destroy();
        }
        internal function frame_30():* {
            if (this.self == null)
                        {
                            this.self = SSF2API.getProjectile(this);
                        };
                        this.self.stancePlayFrame("suspend");
        }
        internal function frame_31():* {
            this.self = SSF2API.getProjectile(this);
                        this.isOnGround = false;
                        if (SSF2API.isReady() && this.self)
                        {
                            this.character = this.self.getOwner();
                            this.self.updateAttackBoxStats(1, {"effectSound":"brawl_fire_l"});
                            this.self.addEventListener(SSF2Event.ATTACK_CONNECT, this.toContinue);
                            this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.toContinue);
                            this.self.addEventListener(SSF2Event.ATTACK_HIT_POWER_SHIELD, this.self.flip);
                            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toContinue);
                            this.self.addEventListener(SSF2Event.HIT_WALL, this.toContinue);
                            this.self.addEventListener(SSF2Event.REVERSE, this.self.flip);
                            this.self.playSound("bmfire");
                            this.self.stancePlayFrame("loop");
                        };
        }
    }
}
