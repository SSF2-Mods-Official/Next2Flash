package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class bm_bthrowrock_155 extends MovieClip {
        public var hitBox:MovieClip;
        public var self:*;
        public var character:*;
        public var isOnGround:*;
        public function bm_bthrowrock_155() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(3, frame_4);
            addFrameScript(23, frame_24);
        }
        internal function frame_1():* {
            var hitBox:MovieClip;
            var self:*;
            var character:*;
            var isOnGround:*;
            this.self = SSF2API.getProjectile(this);
                        if (SSF2API.isReady() && this.self)
                        {
                            this.character = this.self.getOwner();
                        };
                        this.visible = false;
                        this.isOnGround = false;
                        if (SSF2API.isReady() && this.self)
                        {
                            this.character.setGlobalVariable("bthrowProjectileDied", false);
                        };
        }
        internal function frame_4():* {
            this.isOnGround = this.self.isOnGround();
                        if (!this.isOnGround)
                        {
                            this.character.setGlobalVariable("bthrowProjectileDied", true);
                            this.self.destroy();
                        };
                        this.visible = true;
        }
        internal function frame_24():* {
            this.self.destroy();
        }
    }
}
