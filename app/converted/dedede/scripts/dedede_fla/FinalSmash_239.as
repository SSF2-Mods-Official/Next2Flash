package dedede_fla
{
    import flash.display.MovieClip;

    public dynamic class FinalSmash_239 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var camBox:MovieClip;
        public var grabBox:MovieClip;
        public var touchBox:MovieClip;
        public var self:DededeExt;
        public var timesLooped:Number;
        public var timesFired:Number;
        public var camera:*;
        public var enemy:Object;

        public function FinalSmash_239()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 4, this.frame5, 20, this.frame21, 31, this.frame32, 32, this.frame33, 34, this.frame35, 38, this.frame39, 39, this.frame40, 42, this.frame43, 43, this.frame44, 44, this.frame45, 48, this.frame49, 49, this.frame50, 52, this.frame53, 53, this.frame54, 54, this.frame55, 55, this.frame56, 56, this.frame57, 57, this.frame58, 58, this.frame59, 59, this.frame60, 60, this.frame61, 61, this.frame62, 66, this.frame67, 67, this.frame68, 79, this.frame80, 83, this.frame84, 87, this.frame88, 92, this.frame93, 97, this.frame98, 139, this.frame140, 140, this.frame141, 141, this.frame142, 154, this.frame155, 183, this.frame184, 184, this.frame185);
        }

        public function spinToWin():void
        {
            if (this.timesLooped > 6)
            {
                this.self.destroyTimer(this.spinToWin);
            };
        }

        public function dededeMissiles():void
        {
            if (this.timesLooped > 2)
            {
                this.self.destroyTimer(this.dededeMissiles);
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

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as DededeExt);
            if (SSF2API.isReady())
            {
                this.timesLooped = 0;
                this.timesFired = 0;
                this.camera = SSF2API.getCamera();
                this.self.swapDepthsWithGrabbedOpponent(false);
                this.enemy = this.self.getGrabbedOpponent();
                this.camera.killDarkener(true);
                this.self.resetMovement();
                this.self.camFocus(30);
            };
        }

        internal function frame2():*
        {
            if (!this.self.getMetalStatus())
            {
                this.self.playSound("ssf2_snd_vfx_dedede_final_end", true);
            };
        }

        internal function frame5():*
        {
            this.self.playSound("throw_woosh");
        }

        internal function frame21():*
        {
            this.self.playSound("grab");
            SSF2API.getCamera().shake(4);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_l");
            }
            else
            {
                this.self.playSound("ssf2_snd_sfx_dedede_landHeavy");
            };
        }

        internal function frame32():*
        {
            if (!this.self.isOnGround())
            {
                this.self.setXSpeed(15, false);
            }
            else
            {
                this.self.setXSpeed(15, false);
            };
        }

        internal function frame33():*
        {
            this.self.updateAttackStats({
                "allowControlGround":true,
                "allowControl":true
            });
        }

        internal function frame35():*
        {
            this.self.swapDepths(this.enemy);
            this.self.playSound("ssf2_snd_sfx_dedede_swing_m");
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-26),
                "y":3,
                "scaleX":1,
                "scaleY":1
            });
        }

        internal function frame39():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":3,
                "hitLag":-1.3,
                "hitStun":4,
                "selfHitStun":0,
                "effectSound":"ssf2_snd_sfx_dedede_hit_m",
                "effect_id":"effect_heavyHit"
            });
            this.self.refreshAttackID();
        }

        internal function frame40():*
        {
            this.self.swapDepths(this.enemy);
            this.self.playSound("ssf2_snd_sfx_dedede_swing_m");
            this.self.attachEffect("global_dust_heavy_rv", {
                "x":this.self.flipX(26),
                "y":3,
                "scaleX":1,
                "scaleY":1
            });
        }

        internal function frame43():*
        {
            this.self.swapDepths(this.enemy);
        }

        internal function frame44():*
        {
            this.self.refreshAttackID();
        }

        internal function frame45():*
        {
            this.self.playSound("ssf2_snd_sfx_dedede_swing_m");
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-26),
                "y":3,
                "scaleX":1,
                "scaleY":1
            });
        }

        internal function frame49():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":2,
                "hitLag":-1.3,
                "hitStun":4,
                "selfHitStun":0,
                "effectSound":"ssf2_snd_sfx_dedede_hit_m",
                "effect_id":"effect_heavyHit"
            });
            this.self.refreshAttackID();
        }

        internal function frame50():*
        {
            this.self.swapDepths(this.enemy);
            this.self.playSound("ssf2_snd_sfx_dedede_swing_m");
            this.self.attachEffect("global_dust_heavy_rv", {
                "x":this.self.flipX(26),
                "y":3,
                "scaleX":1,
                "scaleY":1
            });
        }

        internal function frame53():*
        {
            this.self.refreshAttackID();
            this.self.swapDepths(this.enemy);
        }

        internal function frame54():*
        {
            this.self.playSound("ssf2_snd_sfx_dedede_swing_m");
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-26),
                "y":3,
                "scaleX":1,
                "scaleY":1
            });
        }

        internal function frame55():*
        {
            this.self.refreshAttackID();
        }

        internal function frame56():*
        {
            this.self.createTimer(1, -1, this.spinToWin);
            this.self.swapDepths(this.enemy);
            this.self.playSound("ssf2_snd_sfx_dedede_swing_m");
            this.self.attachEffect("global_dust_heavy_rv", {
                "x":this.self.flipX(26),
                "y":3,
                "scaleX":1,
                "scaleY":1
            });
        }

        internal function frame57():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":0.5,
                "effectSound":"ssf2_snd_sfx_dedede_hit_m",
                "effect_id":"effect_heavyHit"
            });
            this.self.refreshAttackID();
        }

        internal function frame58():*
        {
            this.self.swapDepths(this.enemy);
            this.self.playSound("ssf2_snd_sfx_dedede_swing_s");
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-26),
                "y":3,
                "scaleX":1,
                "scaleY":1
            });
        }

        internal function frame59():*
        {
            this.self.refreshAttackID();
            this.self.swapDepths(this.enemy);
            this.self.playSound("ssf2_snd_sfx_dedede_swing_s");
            this.self.attachEffect("global_dust_heavy_rv", {
                "x":this.self.flipX(26),
                "y":3,
                "scaleX":1,
                "scaleY":1
            });
        }

        internal function frame60():*
        {
            if (this.timesLooped < 15)
            {
                this.timesLooped++;
                this.self.stancePlayFrame("loop");
            }
            else if (this.timesLooped > 15)
            {
                this.self.stancePlayFrame("spin_End");
            };
        }

        internal function frame61():*
        {
            if (!(this.self.getGrabbedOpponents()[0]))
            {
                this.self.stancePlayFrame("fail");
            };
            this.self.updateAttackStats({
                "allowControlGround":false,
                "allowControl":false
            });
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-26),
                "y":3,
                "scaleX":1.25,
                "scaleY":1.25
            });
        }

        internal function frame62():*
        {
            this.self.swapDepths(this.enemy);
        }

        internal function frame67():*
        {
            this.self.updateAttackBoxStats(1, {
                "damage":10,
                "canDI":false,
                "hitLag":-1.4,
                "hitStun":5,
                "selfHitStun":3,
                "direction":65,
                "power":65,
                "kbConstant":100,
                "stackKnockback":false,
                "hasEffect":true,
                "effectSound":"ssf2_snd_sfx_dedede_hit_l",
                "effect_id":"effect_heavyHit"
            });
            this.self.refreshAttackID();
            this.self.swapDepths(this.enemy);
        }

        internal function frame68():*
        {
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-26),
                "y":3,
                "scaleX":2,
                "scaleY":2
            });
            this.self.playSound("ssf2_snd_sfx_dedede_swing_ll");
        }

        internal function frame80():*
        {
            this.self.playSound("ssf2_snd_sfx_dedede_dspec_start");
        }

        internal function frame84():*
        {
            this.self.createTimer(1, -1, this.dededeMissiles);
        }

        internal function frame88():*
        {
            this.self.fireProjectile("homingmissile", -16, -35);
            this.self.playSound("ssf2_snd_sfx_dedede_dspec_weak");
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-26),
                "y":3,
                "scaleX":1.25,
                "scaleY":1.25
            });
        }

        internal function frame93():*
        {
            if (this.timesFired < 3)
            {
                this.timesFired++;
                this.self.stancePlayFrame("missile_Fire");
            };
        }

        internal function frame98():*
        {
            this.self.fireProjectile("bigHomingMissile", -16, -35);
            this.self.playSound("ssf2_snd_sfx_dedede_dspec_strong");
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(-26),
                "y":3,
                "scaleX":2,
                "scaleY":2
            });
        }

        internal function frame140():*
        {
            this.self.forceOnGround(5);
            if (!this.self.isOnGround())
            {
                this.self.updateAttackStats({"allowControl":true});
                this.self.resetJumps();
                this.self.toJump();
            };
        }

        internal function frame141():*
        {
            this.self.endAttack();
        }

        internal function frame142():*
        {
            this.self.updateAttackStats({
                "allowControlGround":false,
                "allowControl":false
            });
        }

        internal function frame155():*
        {
            if (this.self.isOnGround())
            {
                SSF2API.getCamera().shake(6);
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_l");
                }
                else
                {
                    this.self.playSound("ssf2_snd_sfx_dedede_uspec_longfail_01");
                };
            };
        }

        internal function frame184():*
        {
            this.self.forceOnGround(5);
            if (!this.self.isOnGround())
            {
                this.self.updateAttackStats({"allowControl":true});
                this.self.resetJumps();
                this.self.toJump();
            };
        }

        internal function frame185():*
        {
            this.self.endAttack();
        }


    }
}

