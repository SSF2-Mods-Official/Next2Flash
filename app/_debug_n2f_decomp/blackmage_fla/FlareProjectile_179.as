package blackmage_fla {
    import flash.display.DisplayObject;
    import flash.display.MovieClip;
    import flash.events.Event;
    public dynamic class FlareProjectile_179 extends MovieClip {
        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var self:*;
        public function FlareProjectile_179() {
            super();
            addFrameScript(0, frame_1);
            addFrameScript(30, frame_31);
            addFrameScript(55, frame_56);
            addFrameScript(97, frame_98);
        }
        internal function frame_1():* {
            var attackBox:MovieClip;
            var attackBox2:MovieClip;
            var self:*;
            this.self = SSF2API.getProjectile(this);
                        if (SSF2API.isReady() && this.self)
                        {
                            this.self.updateAttackStats({"refreshRate":1});
                            this.self.addToCamera();
                        };
        }
        internal function frame_31():* {
            this.self.updateAttackStats({"refreshRate":999});
                        this.self.updateAttackBoxStats(1, {
                            "hasEffect":true,
                            "damage":26,
                            "hitStun":6,
                            "selfHitStun":6,
                            "direction":30,
                            "power":90,
                            "kbConstant":100,
                            "effectSound":"brawl_bomb_l",
                            "effect_id":"effect_explosion"
                        });
                        this.self.updateAttackBoxStats(2, {
                            "hasEffect":true,
                            "damage":26,
                            "hitStun":6,
                            "selfHitStun":6,
                            "direction":30,
                            "power":90,
                            "kbConstant":100,
                            "effectSound":"brawl_bomb_l",
                            "effect_id":"effect_explosion"
                        });
                        this.self.refreshAttackID();
        }
        internal function frame_56():* {
            this.self.removeFromCamera();
        }
        internal function frame_98():* {
            this.self.destroy();
        }
    }
}
