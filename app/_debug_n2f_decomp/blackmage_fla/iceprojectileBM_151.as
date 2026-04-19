package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class iceprojectileBM_151 extends MovieClip {
        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var self:*;
        public var isOnGround:Boolean;
        public var isLeft:Boolean;
        public var newProjectile:*;
        public var keepNext:Boolean;
        public var character:*;
        public var _local_1:* = this.self.getX();
        public var _local_2:* = this.self.getY();
        public var _local_3:* = 55;
        public function iceprojectileBM_151() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(1, frame_2);
            addFrameScript(3, frame_4);
            addFrameScript(8, frame_9);
            addFrameScript(9, frame_10);
            addFrameScript(16, frame_17);
            addFrameScript(20, frame_21);
            addFrameScript(25, frame_26);
            addFrameScript(26, frame_27);
            addFrameScript(27, frame_28);
            addFrameScript(28, frame_29);
            addFrameScript(29, frame_30);
            addFrameScript(31, frame_32);
            addFrameScript(32, frame_33);
            addFrameScript(34, frame_35);
            addFrameScript(51, frame_52);
            addFrameScript(52, frame_53);
            addFrameScript(55, frame_56);
        }
        internal function frame_1():* {
            var attackBox:MovieClip;
            var hitBox:MovieClip;
            var self:*;
            var isOnGround:Boolean;
            var isLeft:Boolean;
            var newProjectile:*;
            var keepNext:Boolean;
            var character:*;
            var _local_1:* = this.self.getX();
            var _local_2:* = this.self.getY();
            var _local_3:* = 55;
            this.self = SSF2API.getProjectile(this);
                        this.isOnGround = true;
                        this.isLeft = false;
                        this.keepNext = false;
                        if (SSF2API.isReady() && this.self)
                        {
                            this.character = this.self.getOwner();
                            this.visible = false;
                            if (!this.self.isFacingRight())
                            {
                                this.self.updateAttackBoxStats(1, {"direction":95});
                            };
                            this.self.addEventListener(SSF2Event.PROJ_DESTROYED, this.toEnd);
                            this.self.addEventListener(SSF2Event.ATTACK_HIT_POWER_SHIELD, this.shieldIt);
                            this.self.addEventListener(SSF2Event.REVERSE, this.reverseIt);
                        };
        }
        internal function frame_2():* {
            this.self.createTimer(1, 20, this.killIt, false);
        }
        internal function frame_4():* {
            if (!this.self.inState(PState.DEAD))
                        {
                            this.visible = true;
                        };
        }
        internal function frame_9():* {
            SSF2API.getCamera().shake(3);
        }
        internal function frame_10():* {
            this.self.playSound("iceshoot2");
                        this.shootIt();
        }
        internal function frame_17():* {
            this.keepNext = true;
        }
        internal function frame_21():* {
            this.self.setXSpeed(0);
                        this.self.setYSpeed(0);
                        this.self.updateProjectileStats({"maxgravity":0});
        }
        internal function frame_26():* {
            this.self.destroy();
        }
        internal function frame_27():* {
            this.self.setGlobalVariable("streamEndProjectile1", true);
                        SSF2API.print("Stream 1 down!");
                        this.self.destroy();
        }
        internal function frame_28():* {
            this.self = SSF2API.getProjectile(this);
                        this.isOnGround = true;
                        this.isLeft = true;
                        this.keepNext = false;
                        if (SSF2API.isReady() && this.self)
                        {
                            this.character = this.self.getOwner();
                            this.visible = false;
                            if (this.self.isFacingRight())
                            {
                                this.self.updateAttackBoxStats(1, {"direction":95});
                            };
                            this.self.addEventListener(SSF2Event.PROJ_DESTROYED, this.toEnd);
                            this.self.addEventListener(SSF2Event.ATTACK_HIT_POWER_SHIELD, this.shieldIt);
                            this.self.addEventListener(SSF2Event.REVERSE, this.reverseIt);
                        };
        }
        internal function frame_29():* {
            this.self.stancePlayFrame("start");
        }
        internal function frame_30():* {
            if ((this.newProjectile != null) && !(this.keepNext))
                        {
                            this.newProjectile.destroy();
                        };
        }
        internal function frame_32():* {
            if (this.self == null)
                        {
                            this.self = SSF2API.getProjectile(this);
                        };
                        this.self.stancePlayFrame("susloop");
        }
        internal function frame_33():* {
            this.self = SSF2API.getProjectile(this);
                        this.isOnGround = true;
                        this.isLeft = false;
                        this.keepNext = false;
                        if (SSF2API.isReady() && this.self)
                        {
                            this.character = this.self.getOwner();
                            this.isLeft = (!(this.character.isFacingRight()));
                            this.self.addEventListener(SSF2Event.ATTACK_HIT_POWER_SHIELD, this.shieldIt);
                            this.self.addEventListener(SSF2Event.REVERSE, this.reverseIt);
                            if (this.character.isOnGround())
                            {
                                this.visible = false;
                                this.self.addEventListener(SSF2Event.PROJ_DESTROYED, this.toEnd);
                            }
                            else
                            {
                                this.isOnGround = false;
                                this.self.updateProjectileStats({
                                    "gravity":1,
                                    "maxgravity":12
                                });
                                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.landIt);
                                this.self.stancePlayFrame("chibair");
                            };
                        };
        }
        internal function frame_35():* {
            this.self.stancePlayFrame("start");
        }
        internal function frame_52():* {
            this.self.stancePlayFrame("chibair");
        }
        internal function frame_53():* {
            this.self.playSound("sfx_icehit_s");
        }
        internal function frame_56():* {
            this.self.destroy();
        }
    }
}
