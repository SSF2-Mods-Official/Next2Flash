package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class ItemFireDash_100 extends MovieClip {
        public var attackBox:MovieClip;
        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;
        public function ItemFireDash_100() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(6, frame_7);
            addFrameScript(8, frame_9);
            addFrameScript(10, frame_11);
            addFrameScript(16, frame_17);
            addFrameScript(17, frame_18);
            addFrameScript(24, frame_25);
        }
        internal function frame_1():* {
            var attackBox:MovieClip;
            var hand:MovieClip;
            var hitBox:MovieClip;
            var hitBox2:MovieClip;
            var hitBox3:MovieClip;
            var itemBox:MovieClip;
            var self:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
                        if (SSF2API.isReady() && this.self)
                        {
                            this.self.setLandingLag(true);
                            this.self.playSound("sonic_shieldfire_dash");
                        };
        }
        internal function frame_7():* {
            this.self.updateAttackStats({
                            "air_ease":-1,
                            "allowControl":true,
                            "allowFastFall":false
                        });
        }
        internal function frame_9():* {
            this.self.updateAttackStats({"allowFastFall":true});
        }
        internal function frame_11():* {
            this.self.setLandingLag(false);
        }
        internal function frame_17():* {
            this.self.endAttack();
        }
        internal function frame_18():* {
            SSF2API.getCamera().shake(3);
                        if (this.self.getMetalStatus())
                        {
                            this.self.playSound("metal_land_m");
                        }
                        else
                        {
                            this.self.playSound("blackmage_landHeavy");
                        };
        }
        internal function frame_25():* {
            this.self.endAttack();
        }
    }
}
