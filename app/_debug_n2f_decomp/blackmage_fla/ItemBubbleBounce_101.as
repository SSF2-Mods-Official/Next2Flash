package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class ItemBubbleBounce_101 extends MovieClip {
        public var attackBox:MovieClip;
        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public var speed:*;
        public var bounceSpeed:*;
        public var _local_1:* = this.self.getCharacterStat("jumpSpeedList").split(",");
        public function ItemBubbleBounce_101() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(12, frame_13);
            addFrameScript(13, frame_14);
            addFrameScript(25, frame_26);
        }
        internal function frame_1():* {
            var attackBox:MovieClip;
            var hand:MovieClip;
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            var speed:*;
            var bounceSpeed:*;
            var _local_1:* = this.self.getCharacterStat("jumpSpeedList").split(",");
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        this.speed = 0;
                        this.bounceSpeed = 0;
                        if (SSF2API.isReady() && this.self)
                        {
                            this.self.createTimer(1, -1, this.setSpeed);
                            this.self.addEventListener(SSF2Event.ATTACK_CONNECT, this.bounce);
                            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.bounce);
                        };
        }
        internal function frame_13():* {
            this.self.stancePlayFrame("fallLoop");
        }
        internal function frame_14():* {
            this.self.updateAttackStats({
                            "xSpeedCap":-1,
                            "xSpeedAccel":0,
                            "xSpeedAccelAir":0,
                            "xSpeedDecay":0,
                            "xSpeedDecayAir":0
                        });
        }
        internal function frame_26():* {
            this.self.endAttack();
        }
    }
}
