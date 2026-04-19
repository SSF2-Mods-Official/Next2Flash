package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class HolyProjectile_177 extends MovieClip {
        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var attackBox3:MovieClip;
        public var self:*;
        public var character:*;
        public var temp:*;
        public var _local_2:Number = NaN;
        public var _local_3:Number = NaN;
        public function HolyProjectile_177() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(14, frame_15);
            addFrameScript(44, frame_45);
            addFrameScript(54, frame_55);
        }
        internal function frame_1():* {
            var attackBox:MovieClip;
            var attackBox2:MovieClip;
            var attackBox3:MovieClip;
            var self:*;
            var character:*;
            var temp:*;
            var _local_2:Number = NaN;
            var _local_3:Number = NaN;
            this.self = SSF2API.getProjectile(this);
                        if (SSF2API.isReady() && this.self)
                        {
                            this.character = this.self.getOwner();
                            this.self.addToCamera();
                            this.self.updateAttackStats({"refreshRate":1});
                            this.self.playSound("magic_screech");
                            this.self.createTimer(1, 0, this.pullInCharacters);
                        };
        }
        internal function frame_15():* {
            this.self.updateAttackStats({"refreshRate":2});
                        this.self.updateAttackBoxStats(1, {
                            "damage":2,
                            "hitStun":0,
                            "direction":140,
                            "canDI":false,
                            "power":140,
                            "kbConstant":40,
                            "effectSound":"brawl_magic_s",
                            "effect_id":"effect_magichit_light"
                        });
        }
        internal function frame_45():* {
            this.self.destroyTimer(this.pullInCharacters);
        }
        internal function frame_55():* {
            this.self.removeFromCamera();
                        this.self.destroy();
        }
    }
}
