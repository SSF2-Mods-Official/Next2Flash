package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class waterSpoutProjStrong_149 extends MovieClip {
        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var self:*;
        public var newXSpeed:*;
        public var newYSpeed:*;
        public var character:*;
        public function waterSpoutProjStrong_149() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(3, frame_4);
            addFrameScript(7, frame_8);
            addFrameScript(9, frame_10);
            addFrameScript(10, frame_11);
            addFrameScript(13, frame_14);
            addFrameScript(17, frame_18);
        }
        internal function frame_1():* {
            var attackBox:MovieClip;
            var hitBox:MovieClip;
            var self:*;
            var newXSpeed:*;
            var newYSpeed:*;
            var character:*;
            this.self = SSF2API.getProjectile(this);
                        this.newXSpeed = 0;
                        this.newYSpeed = 0;
                        if (SSF2API.isReady() && this.self)
                        {
                            this.character = this.self.getOwner();
                            this.newXSpeed = (0.55 * this.character.getXSpeed());
                            this.newYSpeed = ((0.55 * this.character.getYSpeed()) + this.self.getProjectileStat("yspeed"));
                            this.self.setXSpeed(this.newXSpeed, true);
                            this.self.setYSpeed(this.newYSpeed);
                            this.self.addEventListener(SSF2Event.ATTACK_CONNECT, this.toContinue);
                            this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.toContinue);
                            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toContinue);
                            this.self.addEventListener(SSF2Event.HIT_WALL, this.toContinue);
                        };
        }
        internal function frame_4():* {
            this.self.setXSpeed(0);
                        this.self.setYSpeed(0);
        }
        internal function frame_8():* {
            this.self.destroy();
        }
        internal function frame_10():* {
            if (this.self == null)
                        {
                            this.self = SSF2API.getProjectile(this);
                        };
                        this.self.stancePlayFrame("suspend");
        }
        internal function frame_11():* {
            this.self = SSF2API.getProjectile(this);
                        if (SSF2API.isReady() && this.self)
                        {
                            this.self.addEventListener(SSF2Event.ATTACK_CONNECT, this.toChibtinue);
                            this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.toChibtinue);
                            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toChibtinue);
                            this.self.addEventListener(SSF2Event.HIT_WALL, this.toChibtinue);
                        };
        }
        internal function frame_14():* {
            this.self.setXSpeed(0);
                        this.self.setYSpeed(0);
        }
        internal function frame_18():* {
            this.self.destroy();
        }
    }
}
